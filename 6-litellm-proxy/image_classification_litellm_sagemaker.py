import os 
from litellm import completion
import boto3
import base64
from dotenv import load_dotenv
load_dotenv()


assert os.getenv("AWS_ACCESS_KEY_ID"), "Missing AWS_ACCESS_KEY_ID"
assert os.getenv("AWS_SECRET_ACCESS_KEY"), "Missing AWS_SECRET_ACCESS_KEY"
assert os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION"), "Missing region"

sts = boto3.client("sts")
print("CallerIdentity:", sts.get_caller_identity())

sm = boto3.client("sagemaker")
print("DescribeEndpoint:", sm.describe_endpoint(EndpointName="resnet18-endpoint")["EndpointStatus"])

def load_image_as_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

image_b64 = load_image_as_base64("cat.jpg")  # ảnh cần phân loại

# Truyền ảnh qua “prompt”: LiteLLM sẽ nhét vào template input.content_handler ở trên
resp = completion(
    model="sagemaker/resnet18-endpoint",
    messages=[{"role":"user","content":"Classify this image"}],
    aws_region_name="ap-southeast-1"
)
print(resp["choices"][0]["message"]["content"])
