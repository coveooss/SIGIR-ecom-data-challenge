"""
The script takes recommendation train and test data files, and convert thrm into "prepared" data that
can be directly consumed by session_rec repo to run baselines for the recommendation task.
"""

import json
from pathlib import Path
import pickle

import pandas as pd

# This script uses a subset of session IDs to sub-sample the training data.
# Please change the default 1% ratio below to suit your needs.
TRAIN_RATIO = 0.01

TRAIN_PATH = Path('./session_rec_sigir_data/train/browsing_train.csv')
TEST_PATH = Path('./session_rec_sigir_data/test/rec_test_sample.json')

PREPARED_FOLDER = Path('./session_rec_sigir_data/prepared')
PREPARED_FOLDER.mkdir(parents=True, exist_ok=True)

PREPARED_TRAIN_PATH = PREPARED_FOLDER / 'sigir_train_full.txt'
PREPARED_TEST_PATH = PREPARED_FOLDER / 'sigir_test.txt'
ITEM_LABEL_ENCODING_MAP_PATH = PREPARED_FOLDER / 'item_label_encoding.p'

SessionId = 'SessionId'
ItemId = 'ItemId'
Time = 'Time'


def label_encode_series(series: pd.Series):
    """
    Applies label encoding to a Pandas series and returns the encoded series,
    together with the label to index and index to label mappings.

    :param series: input Pandas series
    :return: Pandas series with label encoding, label-integer mapping and integer-label mapping.
    """
    labels = set(series.unique())
    label_to_index = {l: idx for idx, l in enumerate(labels)}
    index_to_label = {v: k for k, v in label_to_index.items()}
    return series.map(label_to_index), label_to_index, index_to_label


print("\n ========================= generate 'prepared' train ========================")
train_data_df = pd.read_csv(TRAIN_PATH)

session_ids = set(train_data_df['session_id_hash'].unique())
train_cutoff = int(len(session_ids) * TRAIN_RATIO)
train_session_ids = list(session_ids)[:train_cutoff]
train_data_df = train_data_df[train_data_df['session_id_hash'].isin(train_session_ids)]

# Filter out:
# * `remove from cart` events to avoid feeding them to session_rec as positive signals
# * rows with null product_sku_hash
# * sessions with only one action
train_data_df = train_data_df[train_data_df['product_action'] != 'remove']
train_data_df = train_data_df.dropna(subset=['product_sku_hash'])
train_data_df['session_len_count'] = train_data_df.groupby('session_id_hash')['session_id_hash'].transform('count')
train_data_df = train_data_df[train_data_df['session_len_count'] >= 2]

# sort by session, then timestamp
train_data_df = train_data_df.sort_values(['session_id_hash', 'server_timestamp_epoch_ms'], ascending=True)

# Encode labels with integers
item_id_int_series, item_label_to_index, item_index_to_label = label_encode_series(train_data_df.product_sku_hash)
item_string_set = set(item_label_to_index.keys())

# Add tokenized session ID, tokenized item ID, and seconds since epoch time.
train_data_df[SessionId] = train_data_df.groupby([train_data_df.session_id_hash]).grouper.group_info[0]
train_data_df[Time] = train_data_df.server_timestamp_epoch_ms / 1000
train_data_df[ItemId] = item_id_int_series

# Get final dataframe
final_train_df = train_data_df[[SessionId, ItemId, Time]]

# Generate CSV and label encoder
final_train_df.to_csv(PREPARED_TRAIN_PATH, sep='\t', index=False)
pickle.dump(item_index_to_label, ITEM_LABEL_ENCODING_MAP_PATH.open(mode='wb'))
print("Done generating 'prepared' for training")

print("\n ========================= generate 'prepared' test ========================")
with TEST_PATH.open() as f:
    test_data = json.load(f)

test_output = []
dummy_label_item = next(iter(item_string_set))
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

# Create the final dataframe and apply label encoding.
test_output_df = pd.DataFrame(test_output)
test_output_df[ItemId] = test_output_df.ItemId.map(item_label_to_index)
test_output_df.to_csv(PREPARED_TEST_PATH, sep='\t', index=False)
print("Done generating 'prepared' for testing")


