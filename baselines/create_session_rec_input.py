"""
The script takes a recommendation test data file, and convert it into "prepared" data that
can be directly consumed by session_rec repo to run baselines for recommendation task
"""

import pandas as pd

import os
import json
import pickle

TRAIN_PATH = './session_rec_sigir_data/train/browsing_train.csv'
TEST_PATH = './session_rec_sigir_data/test/rec_test.json'

PREPARED_FOLDER = './session_rec_sigir_data/prepared'
if not os.path.exists(PREPARED_FOLDER):
    os.makedirs(PREPARED_FOLDER)
PREPARED_TRAIN_PATH = os.path.join(PREPARED_FOLDER, 'sigir_train_full.txt')
PREPARED_TEST_PATH = os.path.join(PREPARED_FOLDER, 'sigir_test.txt')
ITEM_I2S_MAP_PATH = os.path.join(PREPARED_FOLDER, 'item_i2s.p')

SessionId = 'SessionId'
ItemId = 'ItemId'
Time = 'Time'


def get_converted_to_int(series: pd.Series):
    '''
    Consume a item dataframe series (string) to
    generate string<->integer mapping and
    a new series with integer IDs

    :param series: input dataframe series
    :return: string-integer mappng and the new transformed series
    '''
    series_strings = set(series.unique())
    s2i_map = {s: idx for idx, s in enumerate(series_strings)}
    i2s_map = {v: k for k, v in s2i_map.items()}
    return s2i_map, i2s_map, series.map(s2i_map)


print("\n ========================= generate 'prepared' train ========================")
train_data_df = pd.read_csv(TRAIN_PATH)

# use subset of session IDs to sub-sample training data
# here it is set to 1% of train data
train_ratio = 1
if train_ratio:
    session_ids = set(train_data_df['session_id_hash'].unique())
    train_cutoff = int(len(session_ids) * train_ratio / 100)
    train_session_ids = list(session_ids)[:train_cutoff]
    train_data_df = train_data_df[train_data_df['session_id_hash'].isin(train_session_ids)]

# filter out `remove from cart` events to feed to session_rec as positive signals
train_data_no_remove = train_data_df[train_data_df['product_action'] != 'remove']
# sort by session, then timestamp
train_data_no_remove = train_data_no_remove.sort_values(['session_id_hash', 'server_timestamp_epoch_ms'],
                                                        ascending=True)
# got time!
train_data_no_remove[Time] = (train_data_no_remove.server_timestamp_epoch_ms / 1000)
# map SessionId to int
train_data_no_remove[SessionId] = \
train_data_no_remove.groupby([train_data_no_remove.session_id_hash]).grouper.group_info[0]

# remove product_sku_hash null
train_data_no_remove = train_data_no_remove.dropna(subset=['product_sku_hash'])

# remove all sessions having only 1 event
train_data_no_remove['session_len_count'] = train_data_no_remove.groupby([SessionId])[Time].transform('count')
train_data_no_remove = train_data_no_remove[train_data_no_remove['session_len_count'] >= 2]

# get training item set
item_string_set = set(train_data_no_remove.product_sku_hash.unique())
# map ItemId to int
item_id_s2i_map, item_id_i2s_map, item_id_int_series = get_converted_to_int(train_data_no_remove.product_sku_hash)
pickle.dump(item_id_i2s_map, open(ITEM_I2S_MAP_PATH, "wb"))

train_data_no_remove[ItemId] = item_id_int_series

# get final df
final_train_df = train_data_no_remove[[SessionId, ItemId, Time]]

# generate csv
final_train_df.to_csv(PREPARED_TRAIN_PATH, sep='\t', index=False)
print("Done generating 'prepared' for training")

print("\n ========================= generate 'prepared' test ========================")
with open(TEST_PATH) as f:
    test_data = json.load(f)

test_output = []
dummy_label_item = list(item_string_set)[0]
for idx, query_label in enumerate(test_data):
    query = query_label['query']

    # Here, since we must give a label in order to use session_rec repo, we use a dummy item
    # from train data to fill the label for testing data generation;
    # it is fine since we do not need to obtain the real metrics from the session_rec run,
    # the final metrics will be generated using our own scripts)
    first_label_item = dummy_label_item

    cleaned_query_events = []
    for q in query:
        # Skip if it is an action with no item id or it is remove-from-cart or it is unseen from train data
        if q['product_sku_hash'] is None \
                or q['product_action'] == 'remove' \
                or q['product_sku_hash'] not in item_string_set:
            continue
        q_session_id = idx
        q_session_item = q['product_sku_hash']
        q_session_time = q['server_timestamp_epoch_ms'] / 1000
        q_event = {SessionId: q_session_id,
                   ItemId: q_session_item,
                   Time: q_session_time}
        cleaned_query_events.append(q_event)
    if len(cleaned_query_events) > 0:
        # sessionId is mapped to idx integer
        l_event = {SessionId: idx,
                   ItemId: first_label_item,
                   Time: cleaned_query_events[-1][Time] + 1}
        test_output = test_output + cleaned_query_events
        test_output = test_output + [l_event]

# convert list to df
test_output_df = pd.DataFrame(test_output)
# map string to int for ItemId
test_output_df[ItemId] = test_output_df.ItemId.map(item_id_s2i_map)
test_output_df.to_csv(PREPARED_TEST_PATH, sep='\t', index=False)
print("Done generating 'prepared' for testing")


