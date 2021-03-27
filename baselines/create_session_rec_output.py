"""
The script takes the recommendation result file generated by session_rec baselines and recombine
it with the recommendation test data that is used to run the baselines, and finally
generates a copy of the recommendation test data, appended with a new column containing the prediction items
for each test sample.
"""
import csv
import json
import pickle

TEST_PATH = './session_rec_sigir_data/test/rec_test.json'
TEST_WITH_PREDICTION_PATH = './session_rec_sigir_data/test/rec_test_with_pred.json'
RECOMMENDATION_PATH = './session_rec_sigir_data/prepared/test_single_models_sigir.stamp-init_lr=0.003-n_epochs=10-decay_rate=0.4.csv.Saver@20--.csv'
ITEM_I2S_PATH = './session_rec_sigir_data/prepared/item_i2s.p'

item_i2s_map = pickle.load(open(ITEM_I2S_PATH, "rb"))

with open(TEST_PATH) as f:
    original_test_data = json.load(f)

for d in original_test_data:
    d['prediction'] = []

with open(RECOMMENDATION_PATH) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=";")
    for row in reader:
        idx_in_test_data = int(row['SessionId'])
        recommendation_i = list(map(int, row['Recommendations'].split(',')))
        recommendation_s = [item_i2s_map[i] for i in recommendation_i]
        original_test_data[idx_in_test_data]['prediction'] = recommendation_s

# store the final output file
with open(TEST_WITH_PREDICTION_PATH, 'w') as outfile:
    json.dump(original_test_data, outfile)

print("All done appending prediction to original recommendation test data!")
