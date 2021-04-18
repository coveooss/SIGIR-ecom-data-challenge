"""

    Sample script showing how to submit a prediction json file to the AWS bucket assigned to you for the challenge.
    Credentials are in your sign-up e-mail: please refer to the full project README for the exact format of the file
    and the naming convention you need to respect.

"""

import os
import boto3
from datetime import datetime
from dotenv import load_dotenv
# load envs from env file
load_dotenv(verbose=True, dotenv_path='upload.env')

# env info should be in your env file
BUCKET_NAME = os.getenv('BUCKET_NAME') # you received it in your e-mail
EMAIL = os.getenv('EMAIL') # the e-mail you used to sign up
USER_ID = os.getenv('USER_ID') # you received it in your e-mail
AWS_WRITE_ONLY_KEY = os.getenv('AWS_WRITE_ONLY_KEY') # you received it in your e-mail
AWS_WRITE_ONLY_SECRET = os.getenv('AWS_WRITE_ONLY_SECRET') # you received it in your e-mail


def upload_submission(
        local_file: str,
        task: str
):
    print("Starting submission at {}...\n".format(datetime.utcnow()))
    # instantiate boto3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_WRITE_ONLY_KEY ,
        aws_secret_access_key=AWS_WRITE_ONLY_SECRET,
        region_name='us-west-2'
    )
    # prepare s3 path according to the spec
    s3_file_path = '{}/{}/{}'.format(task, USER_ID, local_file)  # it needs to be like e.g. "rec/id/*.json"
    # upload file
    s3_client.upload_file(local_file, BUCKET_NAME, s3_file_path)
    # say bye
    print("\nAll done at {}: see you, space cowboy!".format(datetime.utcnow()))

    return


if __name__ == "__main__":
    # LOCAL_FILE needs to be a json file with the format email_epoch time in ms - email should replace @ with _
    LOCAL_FILE = '{}_1616887274000.json'.format(EMAIL.replace('@', '_'))
    TASK = 'rec'  # 'rec' or 'cart'
    upload_submission(local_file=LOCAL_FILE, task=TASK)
