import os
import boto3
from keycove import hash
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.api_gateway_authorizer_event import (
    DENY_ALL_RESPONSE,
    APIGatewayAuthorizerTokenEvent,
    APIGatewayAuthorizerResponse,
)

API_KEY_TABLE = os.environ["API_KEY_TABLE"]

table = boto3.resource("dynamodb").Table(API_KEY_TABLE)


@event_source(data_class=APIGatewayAuthorizerTokenEvent)
def lambda_handler(event: APIGatewayAuthorizerTokenEvent, context):
    arn = event.parsed_arn

    api_key_item = table.get_item(Key={"ApiKey": hash(event.authorization_token)})

    # Check for non-existent API key
    if api_key_item.get("Item") is None:
        return DENY_ALL_RESPONSE

    policy = APIGatewayAuthorizerResponse(
        principal_id=f"User::{api_key_item['Item']['Username']}",
        region=arn.region,
        aws_account_id=arn.aws_account_id,
        api_id=arn.api_id,
        stage=arn.stage,
    )

    policy.allow_all_routes()

    return policy.asdict()
