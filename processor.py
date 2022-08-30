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
from sagemaker import image_uris
from sagemaker.processing import Processor, ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.session import Session

# sagemaker session
session = Session()
# environment variable
if 'ROLE' in os.environ and 'BUCKET_NAME' in os.environ:
    pass
else:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
        os.environ['ROLE'] = config['ROLE']
        os.environ["BUCKET_NAME"] = config["BUCKET"]
# input and output path
data_input_path = f"s3://{os.environ['BUCKET_NAME']}/pca-processing/house_pricing.csv"
code_input_path = f"s3://{os.environ['BUCKET_NAME']}/pca-processing/process-data.py"
data_output_path = f"s3://{os.environ['BUCKET_NAME']}/pca-processing"
# upload processing script to s3
session.upload_data(
    bucket=os.environ["BUCKET_NAME"],
    key_prefix=f"pca-processing",
    path="process-data.py"
)
# upload data to s3 
session.upload_data(
    bucket=os.environ['BUCKET_NAME'],
    key_prefix=f"pca-processing",
    path="./data/house_pricing.csv"
)

# retrieve aws docker image url for processing data
def retriev_image_url():
    """
    get image url
    """
    image_url = image_uris.retrieve(
        framework="sklearn",
        version="0.23-1",
        region="us-east-1",
        image_scope="training"
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
        instance_type='ml.m4.xlarge',
        entrypoint=['python', '/opt/ml/processing/input/process-data.py']
    )

    processor.run(
        job_name=f'pca-{strftime("%Y-%m-%d-%H-%M-%S")}',
        inputs=[
           ProcessingInput(
            source=data_input_path,
            destination="/opt/ml/processing/data/",
           ),
           ProcessingInput(
            source=code_input_path,
            destination="/opt/ml/processing/input/"
           )
        ],
        outputs=[
            ProcessingOutput(
                source="/opt/ml/processing/output/test",
                destination=f"{data_output_path}/test",
                output_name="test"
            )
        ],
    )

# handle amazon processing tasks for jobs using ml frameworks 
# provide a script to be run as part of the processing job
def test_script_processor():
    """
    script processor sagemaker
    """

    script_processor = ScriptProcessor(
        role='',
        image_uri='',
        instance_count=1,
        instance_type='ml.m4.xlarge',
        command=''
    )

    script_processor.run(
        code='',
        inputs=[],
        outputs=[],
        job_name=''
    )

# sklearn processor
def test_sklearn_processor():
    """
    sklearn processor
    """

    sklearn_processor = SKLearnProcessor(
        framework_version='sklearn_preprocessing.py',
        role='',
        instance_count=1, 
        instance_type='ml.m4.xlarge',
    )
    sklearn_processor.run(
        code='',
        inputs=[],
        outputs=[],
    )


if __name__=="__main__":
    image_url = retriev_image_url()
    test_base_processor(image_url=image_url)
