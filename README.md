# SIGIR eCOM 2021 Data Challenge Dataset
_Public Data Release 1.0.0_

### Overview
Coveo hosts the 2021 [SIGIR eCom](https://sigir-ecom.github.io/data-task.html) Data Challenge and this repository contains utility 
scripts and information about data preparation and testing for the Challenge: the paper introducing the Challenge 
is available as a draft on [arxiv](https://arxiv.org/abs/2104.09423).

Since the dataset is released to the community for research use even outside of the Data Challenge, 
if you are using the dataset for independent research you can skip the details about evaluation in this README.

_Note: there has been some issues when downloading the file using Safari; we suggest you use Chrome for the download and sign-up
process._

This page is continuously updated: come back often to check for updates on the Data Challenge.

### License

The dataset is available for research and educational purposes at [this page](https://www.coveo.com/en/ailabs/sigir-ecom-data-challenge). To obtain the dataset, 
you are required to fill a form with information about you and your institution, 
and agree to the Terms And Conditions for fair usage of the data. For convenience, Terms And Conditions are also included in a pure `txt` format in this repo: 
usage of the data implies the acceptance of these Terms And Conditions.

If you submit to the 2021 Data Challenge [leaderboard](https://sigir-ecom.github.io/data-task.html), you are _required to release your code under an open source license_.

### Dataset

#### Data Description

The dataset is provided as three big text files (`.csv`) - `browsing_train.csv`, `search_train.csv`, `sku_to_content.csv` - inside a `zip` archive containing an additional copy of the _Terms And Conditions_. The final dataset contains 36M events, and it is the first dataset of this
kind to be released to the research community: please review the [Data Challenge paper](https://arxiv.org/abs/2104.09423) for a comparison with 
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
query_vector | vector | A dense representation of the search query, obtained through standard pre-trained modeling and dimensionality reduction techniques. Please note that this representation is compatible with the one in the catalog file.
product_skus_hash | list | Hashed identifiers of the products in the search response.
clicked_skus_hash | list | Hashed identifiers of the products clicked after issuing the search query.


##### Catalog Metadata

The file `sku_to_content.csv` contains a mapping between (hashed) product identifiers (SKUs) and dense representation
of textual and image meta-data from the actual catalog, for all the SKUs in the training and the Challenge evaluation
dataset (when the information is available).

Field | Type | Description
------------ | ------------- | -------------
product_sku_hash | string | Hashed identifier of product ID (SKU).
category_hash | string | The categories are hashed representations of the category hierarchy, `/`-separated.
price_bucket | int | The product price, provided as a 10-quantile integer.
description_vector | vector | A dense representation of textual meta-data, obtained through standard pre-trained modeling and dimensionality reduction techniques. Please note that this representation is compatible with the one in the search file.
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
* *a cart-abandonment task*, where, given a session containing an add-to-cart event for a product X, a model is asked to predict whether the shopper will buy X or not in that session.

For the recommendation task, there is recent literature on [both](https://arxiv.org/pdf/2009.10002.pdf) [modelling](https://arxiv.org/pdf/2012.09807.pdf) and [empirical analyses](https://arxiv.org/pdf/1910.12781.pdf); 
for the cart-abandonment task, "[Shopper intent prediction from clickstream e‑commerce data with minimal browsing information](https://rdcu.be/b8oqN)" 
is a good overview of clickstream prediction in eCommerce, and provides extensive benchmarks on neural architectures for sequence classification. 
Please refer to the [Data Challenge paper](https://arxiv.org/abs/2104.09423) for a more extensive literature review and discussion of relevant use cases.

#### Evaluation

The `evaluation` folder contains the functions used by the system to evaluate a submission (i.e. a `json` file with labels
attached by a model - see below): use the code freely on your experiments to get a sense of how much you are progressing.

The code implements the metrics described below, which are all standard in the literature. While we _do_ 
recognize the importance of a quantitative evaluation, we also strongly encourage teams to investigate the qualitative
behavior of their models, and include those insights in their papers.


##### Rec

We follow a standard evaluation protocol where the models are evaluated by "revealing" part of the session, and they are 
asked to predict future sessions. Given in input a sequence of _n_ events, we use two evaluation schemes for the `rec` task:

* the model is evaluated at predicting the immediate next item. We use *MRR* as our main metric;
* the model is evaluated at predicting all subsequent items of the session, up to a maximum of 20 after the current event. We take the *F1* score from *precision@20* and *recall@20* as the final metrics.

While not part of the final ranking, we measure also additional quality factors, interesting for the community 
and industry use cases, such as _coverage@20_ and _popularity bias@20_. When you submit for the `rec` task, the system
will automatically score the submission for both tasks, and we will maintain two leaderboards.

Please note that when a test session includes a search query, this event will be available to the model as an 
input (it can and should be taken into consideration by the model), but it will be ignored when computing the metrics 
when the rest of the session is compared with the recommendations - in other words, we ask models only to predict 
future products, not search events.

##### Cart

Models will be evaluated by the *micro-F1 score* in predicting shopping cart abandonment at the first add-to-cart event (AC), 
and then 2, 4, 6, 8 and 10 events after the first AC. By assessing performance at AC, moreover, 
we want to stress the importance of predicting intent from as little data as relevant. 
Each model will be evaluated by performing a weighted combination of  micro-F1 scores at different clicks, 
with larger weights assigned to earlier predictions according to the following schema:
 
* micro-F1 at AC * 1
* micro-F1 2 clicks after AC * 0.9
* micro-F1 4 clicks after AC * 0.8
* micro-F1 6 clicks after AC * 0.7
* micro-F1 8 clicks after AC * 0.6
* micro-F1 10 clicks after AC * 0.5

The test set will not undergo any resampling to even the class distribution: to avoid trivializing inference, test 
sessions including purchases will be cut before the first purchase event.

Even though this metric is the one on which we determine the winning submission, we encourage submissions 
to present other metrics including AUC, precision and recall for purchase and cart-abandonment prediction, 
as well as measures of how sooner than the session ends the correct prediction is made. 
For example, suppose there are 15 actions after the AC in a purchase session: a model 
which converges on consistently predicting a purchase from action 11 (not captured in our evaluation) would anticipate 
the right outcome more than a model which is undecided until the second-to-last action but still correctly 
predicts a purchase at the end of the session. A measure of anticipation would be very informative although it 
depends on some free parameters (how strong the support for a given prediction should be, for how many consecutive 
ctions it should remain stable, what it means to remain stable, etc.): given these degrees of freedom we decided 
not to make this a ranking criterion, but still would appreciate submissions that show how models behave in this respect.

#### Submission Process

To submit to the Data Challenge, please first visit the [Challenge web-page](https://sigir-ecom.github.io/data-task.html). You will be asked to sign up to
receive your user id and write-only credentials to an AWS S3 bucket, necessary to upload your submission: treat
the credentials with the necessary precautions (please note that the Challenge is hosted on a devoted AWS account, 
which will be deleted at the end of Challenge).

##### Challenge rules

The challenge will happen in two phases:

* in the first phase, you can submit at most 10 submissions per task per day;
* in the second phase, you can submit at most 1 submission per task per day.

The winning team is the team leading the leaderboard when the challenge ends: 
official timelines are on the [SIGIR ecom](https://sigir-ecom.github.io/data-task.html) page.

Finally, a CFP will be issued in the upcoming weeks, encouraging system papers describing models and approaches, as well as 
important qualitative insights on the two tasks.

##### Submission file

Submissions are just json files, which are exactly the same as the test files you are provided with at sign-up,
but containing a `label` field: your model should fill `label` with its predictions, which will be compared
to the ground truth by our script to produce the final metrics, and update the leaderboard. 

For the `rec` task, `label` is expected to be a list of hashed product SKU, as in the mock test case below:

```
{
    "query": [
      {
        "session_id_hash": "bafb7811-482c-4a24-93ea-ab4e40740988",
        "query_vector": null,
        "clicked_skus_hash": null,
        "product_skus_hash": null,
        "server_timestamp_epoch_ms": 1557432435044,
        "event_type": "event_product",
        "product_action": "detail",
        "product_sku_hash": "f7f2c9d7-f0c1-4cdb-9dba-bec424e83ddd",
        "is_search": false
      }
    ],
    "label": [
      "52aa439c-4e14-4a05-8b39-0bed3234d16c",
      "16891170-4e44-4467-af76-169e0f8cc2cd",
    ]
  }
```

For the `cart` task, `label` is expected to be an integer, 
indicating if the session with the add-to-cart event will convert into a purchase (1) or not (0):

```
{
    "query": [
      {
        "session_id_hash": "741d0f9f-5c9b-4ccc-b82f-d73d9a728ec9",
        "query_vector": null,
        "clicked_skus_hash": null,
        "product_skus_hash": null,
        "server_timestamp_epoch_ms": 1556250432707,
        "event_type": "event_product",
        "product_action": "detail",
        "product_sku_hash": "8a373684-51f9-4d04-a0d3-59f46a128ee6",
        "hashed_url": "3919d6e4-3352-404c-9042-86ff2f239fd8",
        "is_search": false
      }
    ],
    "label": 0
  }
```

The file name should have the following format:

`{}_1616887274000.json'.format(EMAIL.replace('@', '_'))`

that is, the sign-up e-mail (with `@` replaced by `_`) and epoch time in milliseconds, joined by a `_`. For example,
a submission for someone having `jtagliabue@coveo.com` as e-mail would look like:

`jtagliabue_coveo.com_1616887274000.json`

The S3 path structure should have the following format:

`rec/49a158cb-510f-4cea-8abe-0a3218d1b5ae/[LOCALFILE]`

that is, the task (`rec` or `cart`), the user id you were provided
with at the sign-up, and the actual `json` file, named according to the rules above. For your convenience,
we provide you with a ready-made script that given a local submission file, performs the upload to the
Challenge bucket (see below).

##### Submission upload

Once ready to be submitted, your test file needs to be uploaded to the S3 bucket provided at sign-up, with the
correct credentials, user id and file structure (see above). 

For your convenience, the script `submission/uploader.py` in this repository can be used to upload your 
json to the correct bucket: make sure to duplicate the `.env.local` file as an `.env` file in this folder, 
and fill it with the information contained in your sign-up e-mail (or alternatively, set up the 
corresponding environment variables). Once you change the `LOCAL_FILE` in `submission/uploader.py`
to the name of the current submission file, running the script from your command line should produce a
successful submission; after metrics calculation, you will also receive an e-mail acknowledging
the submission and reporting the scores.


#### Submission example

The script `submission/p2vec_knn_example.py` is a simple knn model based on 
[product embeddings](https://arxiv.org/abs/2007.14906). If you run the script with `browsing_train.csv`
and `rec_test_phase_1.json` in the same folder, it will produce a local `json` file with labels valid for the
"next prediction event" evaluation: if you then run  `submission/uploader.py` with the appropriate `LOCAL_NAME` and
`env` variables, you will have a valid (albeit far from perfect!) submission.

Similar to the knn model, `submission/cart_example.py` is a simple LSTM-based model that performs binary classification 
of shopping sequences for the 'cart-abandonment' task. If you run the script with `browsing_train.csv`
and `intention_test_phase_1.json` in the same folder, it will produce a local `json` file with labels valid for the
"cart abandonment" evaluation.

These models are provided as additional examples for the submission process (and perhaps, as an easy baseline) 
and it is not intended to be in any way a suggestion on how to tackle the Challenge: for example, the script
`submission/p2vec_knn_example.py` does not perform  the necessary checks on timestamp ordering
(or any other consistency check). 

### Baselines

We adapted the code from [session-rec](https://github.com/rn5l/session-rec) repository, and share in the `baselines`
folder what is necessary to shape the dataset and run the baseline model, which is an in-session recommendation system.

### Contacts

* For questions about using the dataset as part of your research, please reach out to [Jacopo Tagliabue](https://www.linkedin.com/in/jacopotagliabue/).
* For questions about the Challenge, please join the Data Challenge Slack from the challenge [main page](https://sigir-ecom.github.io/data-task.html), and chat with us there.

### Acknowledgments
The SIGIR Data Challenge is a collaboration between industry and academia, over a dataset gently provided by Coveo.
The authors of the paper and organizers are:

* [Jacopo Tagliabue](https://www.linkedin.com/in/jacopotagliabue/) - Coveo AI Labs
* [Ciro Greco](https://www.linkedin.com/in/cirogreco/) - Coveo AI Labs
* [Jean-Francis Roy](https://www.linkedin.com/in/jeanfrancisroy/) - Coveo
* [Federico Bianchi](https://www.linkedin.com/in/federico-bianchi-3b7998121/) - Postdoctoral Researcher at Università Bocconi
* [Giovanni Cassani](https://giovannicassani.github.io/) - Tillburg University
* [Bingqing Yu](https://www.linkedin.com/in/bingqing-christine-yu/) - Coveo
* [Patrick John Chia](https://www.linkedin.com/in/patrick-john-chia-b0a34019b/) - Coveo

The authors wish to thank Richard Tessier and the entire Coveo's legal team, for supporting our research and believing in 
this data sharing initiative; special thanks to [Luca Bigon](https://www.linkedin.com/in/bigluck/) for help in data collection and preparation.

### How to Cite our Work

If you use this dataset, please cite our work:

```
@inproceedings{CoveoSIGIR2021,
author = {Tagliabue, Jacopo and Greco, Ciro and Roy, Jean-Francis and Bianchi, Federico and Cassani, Giovanni and Yu, Bingqing and Chia, Patrick John},
title = {SIGIR 2021 E-Commerce Workshop Data Challenge},
year = {2021},
booktitle = {SIGIR eCom 2021}
}
```
