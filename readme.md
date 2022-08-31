---
title: Api Gateway Socket
description: Just show a simple setup with api gateway socket
author: haimtran
publishedDate: 08/14/2022
date: 2022-08-14
---

## Introduction

[GitHub](https://github.com/entest-hai/sagemaker-sdk-processing) this show an example how to use different processsors provided by SageMaker API.

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
