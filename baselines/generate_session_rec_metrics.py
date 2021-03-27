"""
The script takes the recommendation test data with appended predictions, and compute the final metrics.
Note: some paths pointing to raw training data is needed to be specified, as we need some training data statistic for
some of the metrics, e.g. popularity
"""
import sys

sys.path.append("..")
import os
import json
from test_data_evaluation_metrics import compute_rec_metrics, construct_item_to_pop_map, construct_all_items

if __name__ == "__main__":
    # training file input path

    EVENT_TRAIN_PATH = './session_rec_sigir_data/train/browsing_train.csv'
    SKU_TO_CONTENT_PATH = './session_rec_sigir_data/train/sku_to_content.csv'

    # use the following to run with sample ground truth and prediction files
    ORIGINAL_PATH = './rec_test_gt.json'
    TEST_WITH_PRED_PATH = './rec_test_random_prediction.json'

    # uncomment if you have real ground truth and predictions
    # ORIGINAL_PATH = './session_rec_sigir_data/test/rec_test_gt.json'
    # TEST_WITH_PRED_PATH = './session_rec_sigir_data/test/rec_test_with_pred.json'

    # output path
    EVALUATION_OUTPUT_FOLDER_PATH = './recommendation_eval_output'
    if not os.path.exists(EVALUATION_OUTPUT_FOLDER_PATH):
        os.makedirs(EVALUATION_OUTPUT_FOLDER_PATH)

    SKU_TO_POP_NAME = 'sku_to_pop.p'
    ALL_SKUS_NAME = 'all_skus.p'
    METRICS_NAME = 'result_metrics.json'

    # generate sku to pop
    construct_item_to_pop_map(train_browse_path=EVENT_TRAIN_PATH,
                              output_path=os.path.join(EVALUATION_OUTPUT_FOLDER_PATH, SKU_TO_POP_NAME))

    # generate all train/test skus
    construct_all_items(sku_to_content_path=SKU_TO_CONTENT_PATH,
                        output_path=os.path.join(EVALUATION_OUTPUT_FOLDER_PATH, ALL_SKUS_NAME))

    with open(ORIGINAL_PATH) as f:
        original_test_data = json.load(f)

    with open(TEST_WITH_PRED_PATH) as f:
        prediction_test_data = json.load(f)

    labels = [_['label'] for _ in original_test_data]
    preds = [_['prediction'] for _ in prediction_test_data]

    # set K and generate metrics
    k = 20
    METRIC_TO_SCORE = compute_rec_metrics(preds=preds,
                                          labels=labels,
                                          item_to_pop_path=os.path.join(EVALUATION_OUTPUT_FOLDER_PATH, SKU_TO_POP_NAME),
                                          all_skus_path=os.path.join(EVALUATION_OUTPUT_FOLDER_PATH, ALL_SKUS_NAME),
                                          topK=k)
    print(METRIC_TO_SCORE)
    with open(os.path.join(EVALUATION_OUTPUT_FOLDER_PATH, METRICS_NAME), 'w') as outfile:
        json.dump(METRIC_TO_SCORE, outfile)
