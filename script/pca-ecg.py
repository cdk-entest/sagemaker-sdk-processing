import os
import argparse
from time import strftime
import glob 
from datetime import datetime
import pandas as pd 
from sklearn.decomposition import PCA
import boto3

# container base path 
container_base_path = "/opt/ml/processing"

# output 
os.makedirs(f"{container_base_path}/output", exist_ok=True)

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

# pca 
pca = PCA(n_components=4)

# loop through all input data files 
for file in glob.glob(f"{container_base_path}/data/*.csv"):
    # file name 
    file_name = file.split("/")[-1]
    print(file)
    # read data 
    df = pd.read_csv(file, usecols=[1, 2, 3, 4], dtype=float)
    # remove nan
    df.fillna(0.0, inplace=True)
    # to array 
    ecg = df.values
    # apply pca 
    pecg = pca.fit_transform(ecg)
    # save result 
    pd.DataFrame(pecg).to_csv(f"{container_base_path}/output/pca_{file_name}", header=None, index=None)
    

