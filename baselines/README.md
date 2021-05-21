# In-Session Recommendations - Baseline Model

### Overview
As part of the data release for the 2021 [SIGIR eCom](https://sigir-ecom.github.io/) Data Challenge, 
to help practitioners evaluating their submission we also provide some utility scripts to run code 
from the paper ["Session-aware Recommendation: A Surprising Quest for the State-of-the-art"](https://arxiv.org/pdf/2011.03424.pdf), as released in the [session-rec](https://github.com/rn5l/session-rec) repo.

### Run Session-Rec

To run _session-rec_ on our dataset, we distinguish three phases:

* prepare input data in the requested format;
* run the actual model;
* evaluate the predictions with the Data Challenge metrics.

#### Data Preparation
First, go into the `baselines` directory as the root directory. 

* replace the sample files in `session_rec_sigir_data/train` with the actual dataset. These files will be transformed to become _session-rec_ training dataset;
* replace `rec_test_sample.json` in `session_rec_sigir_data/test` with the test cases you want the model to predict (note: this should be the same `json` format as the one for the Data Challenge);
* run the `create_session_rec_input.py` script (you can modify the `train_ratio` in `create_session_rec_input.py`, to use a larger/smaller ratio of the training data for session_rec);

At the end of the script, a `prepared` folder will be created into your `session_rec_sigir_data` folder, containing the data in the requested format to run the model.

#### Run the Model

First, get the model code by cloning the repo `https://github.com/rn5l/session-rec` ([paper](https://arxiv.org/pdf/2011.03424.pdf)), that is compatible with Python 3.8 and below. 
Make sure to install the requirements. You might need to install the packages listed in `requirements_conda.txt` even if you do not use Conda. Now you are ready to run the model on the previously prepared data: 

* copy+paste the `session_rec_sigir_data` folder (from the previous section) inside the `data` folder;
* copy+paste our `example_sigir.yml` inside the `conf` folder;
* run `python run_config.py conf/example_sigir.yml`;
* go to the `results/last/sigir` folder, choose a csv file ending with `Saver@` and copy it;
* paste the csv into the `session_rec_sigir_data/prepared` folder.  

#### How to Combine the Predictions with Coveo Test Dataset

We are now ready to generate a `json` file compatible with our evaluation script: 
use the `baselines` directory as the root directory. 

* open `create_session_rec_output.py` script, set the `RECOMMENDATION_PATH` variable to the path pointing to the csv you just
pasted into `session_rec_sigir_data/prepared`;
* run `python create_session_rec_output.py`;
* at the end of the run, a file named `rec_test_with_pred.json` with a prediction field for each
test sample will be generated and saved in `session_rec_sigir_data/test` folder.

To evaluate the submission, please refer to the standard evaluation scripts, 
as detailed in the Data Challenge README.

### Contacts

For questions about the baseline scripts, please reach out to [Bingqing Yu](https://www.linkedin.com/in/bingqing-christine-yu/).
