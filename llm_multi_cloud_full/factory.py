from llm.clients.azure_provider import AzureLlmProvider
from llm.clients.aws_provider import AwsLlmProvider
from openai.lib.azure import AsyncAzureOpenAI
import os

def get_azure_instances():
    return [
        AzureLlmProvider(AsyncAzureOpenAI(
            api_version=os.environ["OPENAI_API_VERSION"],
            azure_endpoint=endpoint,
            azure_ad_token_provider=None,
            credential=None,
            azure_deployment="https://cognitiveservices.azure.com/.default",
        ))
        for endpoint in os.environ["AZURE_ENDPOINT_LIST"].split(",")
    ]

def get_provider_pool():
    return {
        "azure": get_azure_instances(),
        "aws": [AwsLlmProvider(region=os.environ.get("AWS_REGION", "us-east-1"))]
    }
