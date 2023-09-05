import os
import argparse
from time import strftime
import glob 
from datetime import datetime
import boto3

# container base path 
container_base_path = "/opt/ml/processing"

def read_parameters():
    parser =  argparse.ArgumentParser()
    parser.add_argument("--bucket", type=str, default="")
    params, _ = parser.parse_known_args()
    return params

# parse arguments 
args = read_parameters()

# bucket name 
bucket = args.bucket

# s3 client 
client = boto3.client("s3")

# loop through all input data files 
for file in glob.glob(f"{container_base_path}/data/*.csv"):
    print(file)
    # put object to s3 
    client.put_object(
        Body="hello",
        Bucket=bucket,
        Key=f'data-processed/{file}{datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")[:-3]}.txt'
    )



