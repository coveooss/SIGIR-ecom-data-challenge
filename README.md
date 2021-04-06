# SIGIR eCOM 2021 Data Challenge Dataset
_Public Data Release 1.0.0_

### Overview
Coveo will host the 2021 [SIGIR eCom](https://sigir-ecom.github.io/) Data Challenge and this repository will contain utility 
scripts and information about data preparation and testing for the Challenge.

Since the dataset is released to the community for research use even outside of the Data Challenge, if you are using the dataset for independent reserach you can skip the
details about evaluation in this README.

This page is a WIP - please come back often in the upcoming weeks to check for updates and for the final dataset.

### License

The dataset is available for research and educational purposes at [this page](https://www.coveo.com/en/ailabs/sigir-ecom-data-challenge). To obtain the dataset, you are required to fill a form with information about you and your institution, 
and agree to the Terms And Conditions for fair usage of the data. For convenience, Terms And Conditions are also included in a pure `txt` format in this repo: 
usage of the data implies the acceptance of these Terms And Conditions. 

If you submit to the 2021 Data Challenge leaderboard, you are _required to release your code under an open source license_.

### Dataset

#### Data Description

The dataset is provided as three big text file (`.csv`) - `browsing_train.csv`, `search_train.csv`, `sku_to_content.csv` - inside a `zip` archive containing an additional copy of the 
_Terms And Conditions_. The final dataset contains 36M events, and it is the first dataset of this
kind to be released to the research community: please review the Data Challenge paper (WIP) for a comparison with 
existing datasets and for the motivations behind the release format. For your convenience, three sample files 
are included in the `start` folder, showcasing the data structure. 
Below, you will find a detailed description for each file.

##### Browsing Events

The file `browsing_train.csv` contains almost 5M anonymized shopping [sessions](https://support.google.com/analytics/answer/2731565?hl=en).
The structure of this dataset is similar to our [Scientific Reports](https://github.com/coveooss/shopper-intent-prediction-nature-2020) data release: 
each row corresponds to a browsing event in a session, containing session and timestamp information, as well as 
(hashed) details on the interaction (was it _purchase_ or a _detail_ event? Was it a simple _pageview_ or a specific
product action?). All data was collected and processed in an anonymized fashion through our standard [SDK](https://docs.coveo.com/en/3188/coveo-for-commerce/tracking-commerce-events):
remember that front-end tracking is by nature imperfect, so small inconsistencies are to be expected.

Field | Type | Description
------------ | ------------- | -------------
session_id_hash | string | Hashed identifier of the shopping session. A session groups together events that are at most 30 minutes apart: if the same user comes back to the target website after 31 minutes from the last interaction, a new session identifier is assigned.
event_type | enum | The type of event according to the [Google Protocol](https://developers.google.com/analytics/devguides/collection/protocol/v1), one of { _pageview_ , _event_ }; for example, an _add_ event can happen on a page load, or as a stand-alone event.
product_action | enum | One of { _detail_, _add_, _purchase_, _remove_, _click_ }. If the field is empty, the event is a simple page view (e.g. the `FAQ` page) without associated products. Please also note that an action involving removing a product from the cart might lead to several consecutive _remove_ events.
product_sku_hash | string | If the event is a _product_ event, hashed identifier of the product in the event.
server_timestamp_epoch_ms | int | Epoch time, in milliseconds. As a further anonymization technique, the timestamp has been shifted by an unspecified amount of weeks, keeping intact the intra-week patterns.
hashed_url | string | Hashed url of the current web page.

Finally, please be aware that a PDP may generate both a _detail_ and a _pageview_ event, and that the order of the events in the 
file is not strictly chronological (refer to the session identifier and the timestamp information to reconstruct the 
actual chain of events for a given session). 

##### Search Events

The file `search_train.csv` contains more than 800k search-based interactions. Each row is a search query event issued by a shopper, which includes an array of (hashed) results returned to the client. We also provide which result(s) have been clicked from the result set, if any. 
By reporting also products seen but not clicked, we hope to inspire clever ways to use negative feedback. 

Field | Type | Description
------------ | ------------- | -------------
session_id_hash | string | Hashed identifier of the shopping session. A session groups together events that are at most 30 minutes apart: if the same user comes back to the target website after 31 minutes from the last interaction, a new session identifier is assigned.
server_timestamp_epoch_ms | int | Epoch time, in milliseconds. As a further anonymization technique, the timestamp has been shifted by an unspecified amount of weeks, keeping intact the intra-week patterns.
query_vector | vector | A dense representation of the search query, obtained through standard pre-trained modeling and dimensionality reduction techniques.
product_skus_hash | string | Hashed identifiers of the products in the search response.
clicked_skus_hash | string | Hashed identifiers of the products clicked after issuing the search query.


##### Catalog Metadata

The file `sku_to_content.csv` contains a mapping between (hashed) product identifiers (SKUs) and dense representation
of textual and image meta-data from the actual catalog, for all the SKUs in the training and the Challenge evaluation
dataset (when the information is available).

Field | Type | Description
------------ | ------------- | -------------
product_sku_hash | string | Hashed identifier of product ID (SKU).
category_hash | string | The categories are hashed representations of a category tree where each level of hierarchy is separated with a `/`.
price_bucket | int | The product price, provided as a 10-quantile integer.
description_vector | vector | A dense representation of textual meta-data, obtained through standard pre-trained modeling and dimensionality reduction techniques.
image_vector| vector | A dense representation of image meta-data, obtained through standard pre-trained modeling and dimensionality reduction techniques.

#### How to Start

Download the `zip` folder and unzip it in your local machine. To verify that all is well, you can run the simple
`start/dataset_stats.py` script in the folder: the script will parse the three files, show some sample rows and 
print out some basic stats and counts (if you don't modify the three paths, it will run on the sample `csv`).

Please remember that usage of this dataset implies acceptance of the  Terms And Conditions: you agree to 
not use the dataset for any other purpose  than what is stated in the Terms and Conditions, 
nor attempt to reverse engineer or de-anonymise the dataset by explicitly or implicitly linking the data 
to any person, brand or legal entity.


### Data Challenge Evaluation

If you are using this dataset for independent research purposes, you can skip this section.

If you are using this dataset for the SIGIR eCom Data Challenge, please read carefully this section, as it
contains information about the two tasks, the evaluation metrics and the submission process.

#### Tasks

The SIGIR Data Challenge will welcome submissions on two separate use cases:

* *a session-based recommendation task*, where a model is asked to predict the next interactions between shoppers and products, based on the previous product interactions and search queries within a session;
* *a cart-abandonment task*, where, given a session containing an add-to-cart event for a product X, 
a model is asked to predict whether the shopper will buy X or not in that session.

#### Evaluation

WIP

#### Submission Process

To submit to the Data Challenge, please first visit the Challenge web-page (TBC). You will be asked to sign up to
receive your user id and write-only credentials to an AWS S3 bucket, necessary to upload your submission: treat
the credentials with the necessary precautions (please note that the Challenge is hosted on a devoted AWS account, 
which will be deleted at the end of Challenge).


##### Challenge rules

WIP

##### Submission file

Submissions are just json files, which are exactly the same as the test files you are provided with at sign-up,
but containing a `label` field: your model should fill `label` with its predictions, which will be compared
to the ground truth by our script to produce the final metrics, and update the leaderboard. The file name
should have the following format:

`{}_1616887274000.json'.format(EMAIL.replace('@', '_'))`

that is, the sign-up e-mail (with `@` replaced by `_`) and epoch time in milliseconds, joined by a `_`.

The S3 path structure should have the following format:

`rec/1/49a158cb-510f-4cea-8abe-0a3218d1b5ae/[LOCALFILE]`

that is, the task (`rec` or `cart`), the phase of the Challenge (`1` or `2`), the user id you were provided
with at the sign-up, and the actual `json` file, named according to the rules above. For your convenience,
we provide you with a read-made script that given a local submission file, proceed with the upload to the
Challenge bucket (see below).

##### Submission upload

Once ready to be submitted, your test file needs to be uploaded to the S3 bucket provided at sign-up, with the
correct credentials, user id and file structure (see above). 

For your convenience, the script `submission/uploader.py` in this repository can be used to upload your 
json to the correct bucket: make sure you have an `upload.env` file in the folder, filled the information 
contained in your sign-up e-mail. Once you change the `LOCAL_FILE` in `submission/uploader.py`
to the name of the current submission file, running the script from your command line should produce a
successful submission; after metrics calculation, you will also receive an e-mail acknowledging
the submission and reporting the scores.


#### Submission example

The script `submission/p2vec_knn_example.py` is a simple knn model based on 
[product embeddings](https://arxiv.org/abs/2007.14906). If you run the script with `browsing_train.csv`
and `rec_test_phase_1.json` in the same folder, it will produce a local `json` file with labels valid for the
"next prediction event" evaluation: if you then run  `submission/uploader.py` with the appropriate `LOCAL_NAME` and
`env` variables, you will have a valid (albeit far from perfect!) submission.

The model is provided as an additional example for the submission process (and perhaps, as an easy baseline) 
and it is not intended to be in any way a suggestion on how to tackle the Challenge: the script does not perform
 the necessary checks on timestamp ordering (or any other consistency check). 

### Baselines

We adapted the code from [session-rec](https://github.com/rn5l/session-rec) repository, and share in the `baselines`
folder what is necessary to shape the dataset and run the baseline model, which is an in-session recommendation system.

### Contacts

For questions about the challenge or the dataset, please reach out to [Jacopo Tagliabue](https://www.linkedin.com/in/jacopotagliabue/).

### Acknowledgments
The SIGIR Data Challenge is a collaboration between industry and academia, over a dataset gently provided by Coveo.
The authors of the paper are:

* [Jacopo Tagliabue](https://www.linkedin.com/in/jacopotagliabue/) - Coveo AI Labs
* [Ciro Greco](https://www.linkedin.com/in/cirogreco/) - Coveo AI Labs
* [Jean-Francis Roy](https://www.linkedin.com/in/jeanfrancisroy/) - Coveo
* [Federico Bianchi](https://www.linkedin.com/in/federico-bianchi-3b7998121/) - Postdoctoral Researcher at Università Bocconi
* [Giovanni Cassani](https://giovannicassani.github.io/) - Tillburg University
* [Bingqing Yu](https://www.linkedin.com/in/bingqing-christine-yu/) - Coveo

The authors wish to thank [Richard Tessier](https://www.linkedin.com/in/richardtessier/) and Coveo's legal team for supporting our research and believing in 
this data sharing initiative; special thanks to [Luca Bigon](https://www.linkedin.com/in/bigluck/) and [Patrick John Chia](https://www.linkedin.com/in/patrick-john-chia-b0a34019b/) for help in data collection and preparation.

### How to Cite our Work

WIP

