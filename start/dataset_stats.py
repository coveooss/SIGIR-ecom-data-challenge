"""

    Simple script to verify the text file you you downloaded are all ok.
    Code optimized for simplicity, not performance ;-)

"""


import csv
from datetime import datetime


# put here the file paths if you did not unzip in same folder
BROWSING_FILE_PATH = 'browsing_train_sample.csv'
SEARCH_TRAIN_PATH = 'search_train_sample.csv'
SKU_2_CONTENT_PATH = 'sku_to_content_sample.csv'


def get_rows(file_path: str, print_limit: int = 2):
    """
    Util function reading the csv file and printing the first few lines out for visual debugging.

    :param file_path: local path to the csv file
    :param print_limit: specifies how many rows to print out in the console for debug
    :return: list of dictionaries, one per each row in the file
    """
    rows = []
    print("\n============== {}".format(file_path))
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            # print out first few lines
            if idx < print_limit:
                print(row)
            rows.append(row)

    return rows


def get_descriptive_stats(
        browsing_train_path : str,
        search_train_path: str,
        sku_2_content_path: str
):
    """
    Simple function showing how to read the main training files, print out some
    example rows, and producing the counts found in the Data Challenge paper.

    We use basic python library commands, optimizing for clarity, not performance.

    :param browsing_train_path: path to the file containing the browsing interactions
    :param search_train_path: path to the file containing the search interactions
    :param sku_2_content_path: path to the file containing the product meta-data
    :return:
    """
    print("Starting our counts at {}".format(datetime.utcnow()))
    # first, just read in the csv files and display some rows
    browsing_events = get_rows(browsing_train_path)
    print("# {} browsing events".format(len(browsing_events)))
    search_events = get_rows(search_train_path)
    print("# {} search events".format(len(search_events)))
    sku_mapping = get_rows(sku_2_content_path)
    print("# {} products".format(len(sku_mapping)))
    # now do some counts
    print("\n\n=============== COUNTS ===============")
    print("# {} of distinct SKUs with interactions".format(
        len(set([r['product_sku_hash'] for r in browsing_events if r['product_sku_hash']]))))
    print("# {} of add-to-cart events".format(sum(1 for r in browsing_events if r['product_action'] == 'add')))
    print("# {} of purchase events".format(sum(1 for r in browsing_events if r['product_action'] == 'purchase')))
    print("# {} of total interactions".format(sum(1 for r in browsing_events if r['product_action'])))
    print("# {} of distinct sessions".format(
        len(set([r['session_id_hash'] for r in browsing_events if r['session_id_hash']]))))
    # now run some tests
    print("\n\n*************** TESTS ***************")
    for r in browsing_events:
        assert len(r['session_id_hash']) == 64
        assert not r['product_sku_hash'] or len(r['product_sku_hash']) == 64
    for p in sku_mapping:
        assert not p['price_bucket'] or float(p['price_bucket']) <= 10
    # say goodbye
    print("All done at {}: see you, space cowboy!".format(datetime.utcnow()))

    return


if __name__ == "__main__":
    get_descriptive_stats(
        BROWSING_FILE_PATH,
        SEARCH_TRAIN_PATH,
        SKU_2_CONTENT_PATH
    )