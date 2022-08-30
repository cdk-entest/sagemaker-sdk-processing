from urllib import response
from sagemaker import image_uris

# retrieve url of a xgboost-neo
response = image_uris.retrieve(
    framework="xgboost-neo",
    region="us-east-1",
)
print(response)

# retrieve url of a pca image
response = image_uris.retrieve(
    framework="pca",
    region="us-east-1"
)
print(response)
