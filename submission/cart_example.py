"""

    Sample script running e-2-e a LSTM model for cart task, including automatically submitting the
    local prediction file to AWS. This is just a sample script provided for your convenience, but it should not
    be treated as a credible baseline.

"""

import os
import time
import json
import csv
from datetime import datetime
from dotenv import load_dotenv
import gensim
from random import choice, shuffle
from uploader import upload_submission

import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import wandb
from wandb.keras import WandbCallback


# load envs from env file
load_dotenv(verbose=True, dotenv_path='upload.env')

# Log In to wandb
# NB : This assumes you have a valid wandb api key stored as WANDB_API_KEY in upload.env
# You may remove/comment out the below line if you do not wish to use wandb
wandb.login()


# read envs from file
EMAIL = os.getenv('EMAIL', None) # the e-mail you used to sign up
assert EMAIL is not None


def read_sessions_from_training_file(training_file: str, K: int = None):
    user_sessions = []
    current_session_id = None
    current_session = []
    with open(training_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            # if a max number of items is specified, just return at the K with what you have
            if K and idx >= K:
                break
            # row will contain: session_id_hash, product_action, product_sku_hash
            _session_id_hash = row['session_id_hash']
            # when a new session begins, store the old one and start again
            if current_session_id and current_session and _session_id_hash != current_session_id:
                user_sessions.append(current_session)
                # reset session
                current_session = []
            # We extract actions from session
            if row['product_action'] == '' and row['event_type'] ==  'pageview':
                current_session.append('view')

            elif row['product_action'] != '':
                current_session.append(row['product_action'])
            # update the current session id
            current_session_id = _session_id_hash

    # print how many sessions we have...
    print("# total sessions: {}".format(len(user_sessions)))
    # print first one to check
    print("First session is: {}".format(user_sessions[0]))

    return user_sessions


def session_indexed(s):
    """
    Converts a session (of actions) to indices and adds start/end tokens

    :param s: list of actions in a session (i.e 'add','detail', etc)
    :return:
    """
    action_to_idx = {'start': 0, 'end': 1, 'add': 2, 'remove': 3, 'purchase': 4, 'detail': 5, 'view': 6}
    return [action_to_idx['start']] + [action_to_idx[e] for e in s] + [action_to_idx['end']]


def prepare_training_data(sessions):
    """

    Convert extracted session into training data

    :param sessions: list of sessions
    :return:
    """

    purchase_sessions = []
    abandon_sessions = []
    for s in sessions:
        if 'purchase' in s and 'add' in s and s.index('purchase') > s.index('add'):
            first_purchase = s.index('purchase')
            p_session = s
            if s.count('purchase') > 1:
                second_purchase = s.index('purchase', first_purchase+1)
                p_session = s[:second_purchase]
            # remove actual purchase from list
            p_session.pop(first_purchase)
            purchase_sessions.append(p_session)
            assert not any( e == 'purchase' for e in p_session)

        elif 'add' in s and not 'purchase' in s:
            abandon_sessions.append(s)

    purchase_sessions = [session_indexed(s) for s in purchase_sessions]
    abandon_sessions = [session_indexed(s) for s in abandon_sessions]

    # combine session with purchase and abandon
    x = purchase_sessions + abandon_sessions

    # give label=1 for purchase, label=0 for abandon
    y = [1]*len(purchase_sessions) +[0]*len(abandon_sessions)
    assert len(x) == len(y)

    return x, y

def train_lstm_model(x, y,
                     epochs=200,
                     patience=10,
                     lstm_dim=48,
                     batch_size=128,
                     lr=1e-3):
    """
    Train an LSTM to predict purchase (1) or abandon (0)

    :param x: session sequences
    :param y: target labels
    :param epochs: num training epochs
    :param patience: early stopping patience
    :param lstm_dim: lstm units
    :param batch_size: batch size
    :param lr: learning rate
    :return:
    """

    # If you do no want to use wandb, you may comment out wandb_config and wandb.init
    # Here store a dictionary of some parameters we may want to track with wandb
    wandb_config = {'epochs' : epochs, 'patience': patience, 'lr' : lr, "lstm_dim": lstm_dim, 'batch_size' : 128}
    # Initialization for a run in wandb
    wandb.init(project="cart-abandonment",
               config=wandb_config,
               id=wandb.util.generate_id())



    X_train, X_test, y_train, y_test = train_test_split(x,y)
    # pad sequences
    max_len = max(len(_) for _ in x)
    X_train = pad_sequences(X_train, padding="post",value=7, maxlen=max_len)
    X_test = pad_sequences(X_test, padding="post", value=7, maxlen=max_len)

    # convert to one-hot
    X_train = tf.one_hot(X_train, depth=7)
    X_test = tf.one_hot(X_test, depth=7)

    y_train = np.array(y_train)
    y_test = np.array(y_test)

    # Define Model
    model = keras.Sequential()
    model.add(keras.layers.InputLayer(input_shape=(None,7)))
    model.add(keras.layers.Masking())
    model.add(keras.layers.LSTM(lstm_dim))
    model.add(keras.layers.Dense(1,activation='sigmoid'))
    model.summary()

    # Some Hyper Params
    opt = keras.optimizers.Adam(learning_rate=lr)
    loss = keras.losses.BinaryCrossentropy()
    es = keras.callbacks.EarlyStopping(monitor='val_loss',
                                       patience=patience,
                                       verbose=1,
                                       restore_best_weights=True)

    # wandb includes callbacks for various deep learning libraries like Keras
    # NB: If you do not want to use wandb, remove WandbCallback from list
    callbacks = [es, WandbCallback()]
    model.compile(optimizer=opt,
                  loss=loss,
                  metrics=['accuracy'])

    # Train Model
    model.fit(X_train,y_train,
              validation_data=(X_test,y_test),
              batch_size=batch_size,
              epochs=epochs,
              callbacks=callbacks)

    # return trained model
    return model


def make_predictions(model, test_file: str):

    with open(test_file) as json_file:
        # read the test cases from the provided file
        test_queries = json.load(json_file)

    X_test = []
    # extract actions from test input
    for t in test_queries:
        session = t['query']
        actions = []
        for e in session:
            # NB : we are disregarding search actions here
            if e['product_action'] == None and e['event_type'] ==  'pageview':
                actions.append('view')
            elif e['product_action'] != None:
                actions.append(e['product_action'])
        X_test.append(actions)

    # Convert to index, pad & one-hot
    max_len = max([len(_) for _ in X_test])
    X_test = [ session_indexed(_) for _ in X_test]
    X_test = pad_sequences(X_test, padding="post", value=7, maxlen=max_len)
    X_test = tf.one_hot(X_test, depth=7)

    # make predictions
    preds = model.predict(X_test,batch_size=128)
    preds = (preds > 0.5).reshape(-1).astype(int).tolist()

    # Convert to required prediction format
    preds = [ {'label':pred} for pred in preds]

    assert len(preds) == len(test_queries)

    return preds


def train_lstm(upload=False):
    print("Starting training at {}...\n".format(datetime.utcnow()))
    #  read sessions in from browsing_train.csv in the folder
    #  to avoid waiting too much, we just train on the first K events
    sessions = read_sessions_from_training_file(
        training_file='browsing_train.csv',
        K=300000)

    x, y = prepare_training_data(sessions)
    lstm_model = train_lstm_model(x,y)
    # Make predictions using model on test data
    preds = make_predictions(lstm_model, test_file='intention_test_phase_1.json')

    # name the prediction file according to the README specs
    local_prediction_file = '{}_{}.json'.format(EMAIL.replace('@', '_'), round(time.time() * 1000))

    # dump to file
    with open(local_prediction_file, 'w') as outfile:
        json.dump(preds, outfile, indent=2)

    # finally, upload the test file using the provided script
    if upload:
        upload_submission(local_file=local_prediction_file, task='cart')
    # bye bye
    print("\nAll done at {}: see you, space cowboy!".format(datetime.utcnow()))

    return


if __name__ == "__main__":
    train_lstm(upload=False)
