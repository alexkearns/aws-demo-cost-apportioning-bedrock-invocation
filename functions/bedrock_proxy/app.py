import boto3
import json
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

import json

bedrock_runtime = boto3.client("bedrock-runtime")
app = APIGatewayRestResolver()


@app.post("/invoke-model")
def invoke_model():
    # Take the body from the API GW proxy event, and re-serialise the body as
    # the Bedrock Runtime API expects `body` as a string
    bedrock_request: dict = app.current_event.json_body
    bedrock_request["body"] = json.dumps(bedrock_request["body"])

    # Make a request against the Bedrock Runtime API
    response = bedrock_runtime.invoke_model(**bedrock_request)
    response_body = response["body"].read().decode("utf-8")

    return response_body


def lambda_handler(event, context: LambdaContext):
    return app.resolve(event, context)
