---
title: sagemaker processing job
description: processing at scale with sagemaker processing job
author: haimtran
publishedDate: 08/14/2022
date: 2022-08-14
---

## Introduction

[GitHub](https://github.com/cdk-entest/sagemaker-sdk-processing) this show how to use different processsors provided by SageMaker API.

- Base Processor
- Script Processor
- Sklearn Processor

We need to

- Choose container either by image url or framework version
- Provide your processing code or event your own container
- Provide data, save, download data from to a s3 bucket

<LinkedImage
  href="https://youtu.be/1CRBSPiGQ9Y"
  height={400}
  alt="SageMaker Processing Api"
  src="/thumbnail/sg-processing-api.png"
/>

## Base processor

the key here is the entrypoint where you put your command to run the code

```py
processor = Processor(
    role=os.environ['ROLE'],
    image_uri=image_url,
    instance_count=1,
    instance_type='ml.m4.xlarge',
    entrypoint=["python", f"{container_base_path}/input/process-data.py",
    "--processor=base-processor"]
)

processor.run(
    job_name=f'processor-{strftime("%Y-%m-%d-%H-%M-%S")}',
    inputs=[
        ProcessingInput(
            source=data_input_path,
            destination=f"{container_base_path}/data/"
        ),
        ProcessingInput(
            source=code_input_path,
            destination=f"{container_base_path}/input/"
        )
    ],
    outputs=[
        ProcessingOutput(
            source=f"{container_base_path}/output/train",
            destination=f"{data_output_path}/train",
            output_name="train",
        ),
        ProcessingOutput(
            source=f"{container_base_path}/output/test",
            destination=f"{data_output_path}/test",
            output_name="test",
        ),
        ProcessingOutput(
            source=f"{container_base_path}/output/validation",
            destination=f"{data_output_path}/validation",
            output_name="validation",
        ),
    ]
)

```

## Script Processor

different from the base professor a) command to run code should be python3 and b) the running code is specified in the run method

```py
script_processor = ScriptProcessor(
    role=os.environ["ROLE"],
    image_uri=image_url,
    instance_count=1,
    instance_type="ml.m4.xlarge",
    command=["python3"],
    env={"PROCESSOR": "script-processor"},
)

script_processor.run(
    job_name=f'script-processor-{strftime("%Y-%m-%d-%H-%M-%S")}',
    code="process-data.py",
    inputs=[
        ProcessingInput(
            source=data_input_path,
            # process-data.py needs to know data here
            destination=f"{container_base_path}/data/",
        ),
        ProcessingInput(
            source=code_input_path,
            destination=f"{container_base_path}/input/",
        ),
    ],
    outputs=[
        ProcessingOutput(
            source=f"{container_base_path}/output/train",
            destination=f"{data_output_path}/train",
            output_name="train",
        ),
        ProcessingOutput(
            source=f"{container_base_path}/output/test",
            destination=f"{data_output_path}/test",
            output_name="test",
        ),
        ProcessingOutput(
            source=f"{container_base_path}/output/validation",
            destination=f"{data_output_path}/validation",
            output_name="validation",
        ),
    ],
)
```

## Sklearn Processor

there is no entrypoint or command here, the code is specified in the run method

```py
sklearn_processor = SKLearnProcessor(
    framework_version="0.20.0",
    role=os.environ["ROLE"],
    instance_count=1,
    instance_type="ml.m4.xlarge",
    env={"PROCESSOR": "sklearn-processor"},
)
sklearn_processor.run(
    job_name=f'sklearn-processor-{strftime("%Y-%m-%d-%H-%M-%S")}',
    code="process-data.py",
    inputs=[
        ProcessingInput(
            source=data_input_path,
            # process-data.py needs to know data located here
            destination=f"{container_base_path}/data/",
        ),
        ProcessingInput(
            source=code_input_path,
            destination=f"{container_base_path}/input/",
        ),
    ],
    outputs=[
        ProcessingOutput(
            source=f"{container_base_path}/output/train",
            destination=f"{data_output_path}/train",
            output_name="train",
        ),
        ProcessingOutput(
            source=f"{container_base_path}/output/test",
            destination=f"{data_output_path}/test",
            output_name="test",
        ),
        ProcessingOutput(
            source=f"{container_base_path}/output/validation",
            destination=f"{data_output_path}/validation",
            output_name="validation",
        ),
    ],
)
```

## PySpark Processor

For big data processing, we can use a PySparkProcessor

```py
    spark_processor = PySparkProcessor(
    base_job_name="sm-spark",
    framework_version="3.1",
    role=os.environ["ROLE"],
    instance_count=2,
    instance_type="ml.m5.xlarge",
    max_runtime_in_seconds=1200)

    # run pyspark script
    spark_processor.run(
    submit_app="./pyspark_process_data.py",
    arguments=[
        "--source_bucket_name",
        source_bucket_name,
        "--dest_bucket_name",
        dest_bucket_name,
    ],
    logs=False)
```

The [pyspark_process_data.py](https://github.com/cdk-entest/sagemaker-sdk-processing/blob/main/pyspark_process_data.py) script just simple read data from S3 using Spark DataFrame, performan some transform, then write to a S3 destination. Please note that this job would take about 10 minutes.

## PCA Transform

Let create a parallel sagemaker job with multiple instances to do PCA transform on ECG signal. First let create a processing script which perform PCA on an ECG numpy array

```py
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
```

Second create a sagemaker processing job using sklearn image

```ts
image_uri = image_uris.retrieve(
  (region = "us-east-1"),
  (framework = "sklearn"),
  (version = "0.23-1")
);
```

Create a sagemaker processing with instance count of 8 because the applied quota. Please check [S3DataDistributionType ](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ProcessingS3Input.html) to see how data files are distributed between instances.

```ts
processor = Processor(
    role=role,
    image_uri=image_uri,
    # check service quota from console depending on instance type
    instance_count=8,
    instance_type="ml.m4.xlarge",
    entrypoint=[
        "python",
        f"{container_base_path}/script/pca-ecg.py",
        f"--bucket={bucket}",
    ],
)
```

Finally run the processing job

```py
# it takes about 5 minutes
processor.run(
    inputs=[
        ProcessingInput(
            source=data_input_path,
            destination=f"{container_base_path}/data/",
            s3_data_distribution_type="ShardedByS3Key",
        ),
        ProcessingInput(
            source=code_input_path,
            destination=f"{container_base_path}/script/",
        ),
    ],
    outputs=[
        ProcessingOutput(
            source=f"{container_base_path}/output/",
            destination=f"{data_output_path}",
            output_name="data-pca",
        )
    ],
    job_name=f'demo-{strftime("%Y-%m-%d-%H-%M-%S")}',
)
```

## Pipe Mode

Processing job support two modes for accessing data from S3

- File Mode => data is downloaded from S3 to container
- Pipe Mode => directly stream data from S3 => need code update

For example

```py
ProcessingInput(
  source=data_input_path,
  # process-data.py needs to know data located here
  destination=f"{container_base_path}/data/",
  # Pipe mode to read directly from S3 => update process-data code
  s3_input_mode="Pipe"
),
```

The process data code udpated

```py
TODO

```

## Entrypoint and CMD

According to Page 74 Getting Started with Containerization

- ENTRYPOINT define the command ==> default /bin/sh -c
- CMD define parameters for the command ==> then overwrite at run time

For example, to run the following

```bash
ping 8.8.8.8 -c 3
```

We can configure ENTRYPOINT and CDM in a Dockerfile as the following

```txt
FROM alpine:latest
ENTRYPOINT ["ping"]
CMD ["8.8.8.8", "-c", "3"]
```

Build a pinger image

```bash
docker image build -t pinger .
```

Then we can over-write the three parameters at run time as the following

```bash
docker container run --rm -it pinger -w 5 127.0.0.1
```

It is possible to over-write the entrypoing

```bash
docker container run --rm -it --entrypoing /bin/sh pinger
```

Please note that the default entrypont is /bin/sh -c when we use only CMD

```txt
FROM alpine:latest
CMD wget -O - http://www.google.com
```

The actualy running command would be

```bash
/bin/sh -c "wget -O - http://www.google.com"
```

## Interative Plot

> [!IMPORTANT]

> To enable interactive plot in sagemaker studio, we need to install [ipympl](https://github.com/matplotlib/ipympl). First, go to the sagemaker studio consoler to install and activate sutdio env

```bash
conda activate studio
```

Second install extension

```bash
conda install -c conda-forge nodejs
jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyter-matplotlib
```

Third install the ipympl from the SageMaker studio system terminal

```bash
pip install ipympl
```

Finally enable it in the notebook by magic cell

```bash
%matplotlib widget
```

## Reference

- [Processing Container Input and Output](https://docs.aws.amazon.com/sagemaker/latest/dg/build-your-own-processing-container.html)

- [File and Pipe Mode](https://aws.amazon.com/about-aws/whats-new/2021/10/amazon-sagemaker-fast-file-mode/)

- [sagemaker session](https://sagemaker.readthedocs.io/en/stable/api/utility/session.html)

- [sagemaker process data docs](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html)

- [sagemaker processing job sdk](https://sagemaker.readthedocs.io/en/stable/amazon_sagemaker_processing.html)

- [sagemaker pipe mode](https://aws.amazon.com/blogs/machine-learning/using-pipe-input-mode-for-amazon-sagemaker-algorithms/)

- [sagemaker spark job](https://sagemaker-examples.readthedocs.io/en/latest/sagemaker_processing/spark_distributed_data_processing/sagemaker-spark-processing.html)

- [sagemaker distributed processing](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/use-sagemaker-processing-for-distributed-feature-engineering-of-terabyte-scale-ml-datasets.html)

- [S3DataDistributionType ](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ProcessingS3Input.html)

- [stackoverflow sagemaker distributed](https://stackoverflow.com/questions/68624368/distributed-processing-aws-sagemaker)

- [s3fs docs](https://s3fs.readthedocs.io/en/latest/)

- [timeout default 24 hours](https://sagemaker.readthedocs.io/en/stable/api/training/processing.html#sagemaker.processing.Processor)

- [timeout limit](https://docs.aws.amazon.com/general/latest/gr/sagemaker.html)

- [service quota](https://docs.aws.amazon.com/general/latest/gr/sagemaker.html)

- [ipympl](https://github.com/matplotlib/ipympl)
