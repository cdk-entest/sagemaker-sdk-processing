---
title: Api Gateway Socket
description: Just show a simple setup with api gateway socket
author: haimtran
publishedDate: 08/14/2022
date: 2022-08-14
---

## Introduction

[GitHub](https://github.com/entest-hai/sagemaker-sdk-processing) this show how to use different processsors provided by SageMaker API.

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

## Reference

- [Processing Container Input and Output](https://docs.aws.amazon.com/sagemaker/latest/dg/build-your-own-processing-container.html)

- [File and Pipe Mode](https://aws.amazon.com/about-aws/whats-new/2021/10/amazon-sagemaker-fast-file-mode/)
