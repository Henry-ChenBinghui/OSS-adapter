from typing import List, Dict
from llm.base_provider import BaseLlmProvider
import boto3
import json

class AwsLlmProvider(BaseLlmProvider):
    def __init__(self, region: str = "us-east-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region)

    async def create_embedding(self, text: str, model: str) -> List[float]:
        raise NotImplementedError("Embedding is not supported in this demo")

    async def create_completion(self, model: str, **kwargs) -> Dict:
        body = {
            "prompt": kwargs.get("prompt", ""),
            "max_tokens_to_sample": kwargs.get("max_tokens", 256),
            "temperature": kwargs.get("temperature", 0.5),
        }
        response = self.client.invoke_model(
            modelId=model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        return {"completion": response_body.get("completion")}
