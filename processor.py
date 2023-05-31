"""
haimtran test different sagemaker processors.
1. sagemaker.processing.Processor
2. SklearnProcessor
3. ScriptProcessor
28 aug 2022
"""
import json
import os
from time import strftime
import concurrent.futures
from sagemaker import image_uris
from sagemaker.processing import (
    Processor,
    ScriptProcessor,
    ProcessingInput,
    ProcessingOutput,
)
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.session import Session

#============================== parameters =========================
# sagemaker session
session = Session()
# environment variables
if "ROLE" in os.environ and "BUCKET_NAME" in os.environ:
    pass
else:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
        os.environ["ROLE"] = config["ROLE"]
        os.environ["BUCKET_NAME"] = config["BUCKET"]
# upload data to s3
data_input_path = f"s3://{os.environ['BUCKET_NAME']}/processing-demo/house_pricing.csv"
# upload code to s3
code_input_path = (
    f"s3://{os.environ['BUCKET_NAME']}/processing-demo/process-data.py"
)
# output data in s3
data_output_path = f"s3://{os.environ['BUCKET_NAME']}/processing-demo"
# sagemaker container paths
container_base_path = "/opt/ml/processing"
#============================== upload to s3 =========================
# upload processing script to s3
session.upload_data(
    bucket=os.environ["BUCKET_NAME"],
    key_prefix=f"processing-demo",
    path="process-data.py",
)
# upload data to s3
session.upload_data(
    bucket=os.environ["BUCKET_NAME"],
    key_prefix=f"processing-demo",
    path="./data/house_pricing.csv",
)
#============================== processors =========================
# retrieve aws docker image url for processing data
def retriev_image_url(region='us-east-1'):
    """
    get image url
    """
    image_url = image_uris.retrieve(
        framework="sklearn",
        version="0.23-1",
        region=region,
        image_scope="training",
    )
    return image_url
# sagemaker base processor
def test_base_processor(image_url):
    """
    base processor sagemaker
    """

    # handle amazon sagemaker processing tasks
    processor = Processor(
        role=os.environ["ROLE"],
        image_uri=image_url,
        instance_count=1,
        instance_type="ml.m4.xlarge",
        entrypoint=[
            "python",
            f"{container_base_path}/input/process-data.py",
            "--processor=base-processor",
        ],
    )

    processor.run(
        job_name=f'processor-{strftime("%Y-%m-%d-%H-%M-%S")}',
        inputs=[
            ProcessingInput(
                source=data_input_path,
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


# handle amazon processing tasks for jobs using ml frameworks
# provide a script to be run as part of the processing job
def test_script_processor(image_url: str):
    """
    script processor sagemaker
    """

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


# sklearn processor
def test_sklearn_processor():
    """
    sklearn processor
    """

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
                # input mode either File or Pipe => change process-data code 
                # to read directly from S3 
                s3_input_mode="Pipe"
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


if __name__ == "__main__":
    image_url = retriev_image_url(region="ap-southeast-1")
    # test_base_processor(image_url=image_url)
    # test_script_processor(image_url=image_url)
    # test_sklearn_processor()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(test_base_processor, image_url)
        executor.submit(test_script_processor, image_url)
        executor.submit(test_sklearn_processor)
