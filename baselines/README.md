# In-Session Recommendations - Baseline Model

### Overview
As part of the data release for the 2021 [SIGIR eCom](https://sigir-ecom.github.io/) Data Challenge, 
to help practitioners evaluating their submission we also provide some utility scripts to  
run code from the paper ["Session-aware Recommendation: A Surprising Quest for the
State-of-the-art"](https://arxiv.org/pdf/2011.03424.pdf), as released in the [session-rec](https://github.com/rn5l/session-rec) repo.

This page is a WIP - please come back often in the upcoming weeks to check for updates.

### Run Session-Rec

To run _session-rec_ on our dataset, we distinguish three phases:

* prepare input data in the requested format;
* run the actual model;
* evaluate the predictions with the Data Challenge metrics.

#### Data Preparation ###
First, go into the `recommendation` directory as the root directory. 

* replace the sample files in `session_rec_sigir_data/train` with the actual dataset. These files will be 
transformed to be _session-rec_ training dataset;
* replace `rec_test_sample.json` in `session_rec_sigir_data/train` with the test cases you want
the model to predict (note: this should be the same `json` format as the one for the Data Challenge);
* run the `create_session_rec_input.py` script (you can modify the `train_ratio` in `create_session_rec_input.py`, 
to use a larger/smaller ratio of the training data for session_rec);

At the end of the script, a `prepared` folder will be created into your `session_rec_sigir_data` folder, containing
the data in the requested format to run the model.

#### Running the Model ###

WIP

#### Evaluation ###

WIP

### Contacts

For questions about the baseline scripts, please reach out to [Bingqing Yu](https://www.linkedin.com/in/bingqing-christine-yu/).
