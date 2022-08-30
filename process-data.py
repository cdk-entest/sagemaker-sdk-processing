"""
haimtran
process data script
"""
import argparse
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

SAGEMAKER_TRAINING = True 

# local data path
if SAGEMAKER_TRAINING:
    # input data
    local_data_path = "/opt/ml/processing/data/house_pricing.csv"
    # output data
    processed_train_dir =  "/opt/ml/processing/output/train"
    os.makedirs(processed_train_dir, exist_ok=True)
    processed_validation_dir =  "/opt/ml/processing/output/validation"
    os.makedirs(processed_validation_dir, exist_ok=True)
    processed_test_dir =  "/opt/ml/processing/output/test"
    os.makedirs(processed_test_dir, exist_ok=True)
else: 
    # input data
    local_data_path = "data/house_pricing.csv"
    # output data
    processed_train_dir = os.path.join(os.getcwd(), "data/processed/train")
    os.makedirs(processed_train_dir, exist_ok=True)
    processed_validation_dir = os.path.join(os.getcwd(), "data/processed/validation")
    os.makedirs(processed_validation_dir, exist_ok=True)
    processed_test_dir = os.path.join(os.getcwd(), "data/processed/test")
    os.makedirs(processed_test_dir, exist_ok=True)


def read_parameters():
    parser =  argparse.ArgumentParser()
    parser.add_argument("--processor", type=str, default='based processor')
    parser.add_argument("--sagemaker", type=bool, default=True)
    params, _ = parser.parse_known_args()
    return params

#======================= parse parameters ==================
args = read_parameters()
print(args)

#======================= load data =========================
# load data
df = pd.read_csv(local_data_path)
print(df.head())
# shift column PRICE to the first position
first_column = df.pop('PRICE')
# insert collumn using
df.insert(0, "PRICE", first_column)
print(df.head())
# split and scaling data
train_size = 0.6
val_size = 0.2
test_size = 0.2
random_seed = 42
#====================== split train data ==================
rest_size = 1.0 - train_size
df_train, df_rest = train_test_split(
    df, 
    test_size=rest_size,
    train_size=train_size, 
    random_state=random_seed
)
#====================== split test data ==================
df_val, df_test = train_test_split(
    df_rest, 
    test_size=(test_size / rest_size),
    train_size=(val_size / rest_size),
    random_state=random_seed
)
# reset index 
df_train.reset_index(inplace=True, drop=True)
df_val.reset_index(inplace=True, drop=True)
df_test.reset_index(inplace=True, drop=True)
train_perc = int(len(df_train)/len(df) * 100)
print(f"training size: {len(df_train)} - {train_perc}% of total")
test_perc = int((len(df_test) / len(df)) * 100)
print(f"test size: {len(df_test)} - {test_perc}% of total")
#====================== scaling train data ==================
print("fitting scaling to training data and transforming dataset ...")
scaler_data = StandardScaler()
# fit scaler to the training data 
df_train_transformed = pd.DataFrame(
    scaler_data.fit_transform(df_train),
    columns=df_train.columns
)
df_train_transformed['PRICE'] = df_train['PRICE']
print(df_train_transformed.head())
#====================== scaling val data ==================
print("transforming validation dataset...")
df_val_transformed = pd.DataFrame(
    scaler_data.transform(df_val),
    columns=df_val.columns
 )
#====================== scaling test data ==================
print("transforming test dataset....")
df_test_transformed = pd.DataFrame(
    scaler_data.transform(df_test),
    columns=df_test.columns
)
df_test_transformed['PRICE'] = df_test['PRICE']
print(df_test_transformed.head())
#====================== save processed data ==================
df_train_transformed.to_csv(f"{processed_train_dir}/{args.processor}-train.csv", sep=',', index=False,header=False)
df_test_transformed.to_csv(f"{processed_test_dir}/{args.processor}-test.csv", sep=',', index=False, header=False)
df_val_transformed.to_csv(f"{processed_validation_dir}/{args.processor}-validation.csv", sep=',', index=False, header=False)


