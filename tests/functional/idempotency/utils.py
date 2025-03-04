import hashlib
from typing import Any, Dict

from botocore import stub

from tests.functional.utils import json_serialize


def hash_idempotency_key(data: Any):
    """Serialize data to JSON, encode, and hash it for idempotency key"""
    return hashlib.md5(json_serialize(data).encode()).hexdigest()


def build_idempotency_put_item_stub(
    data: Dict,
    function_name: str = "test-func",
    handler_name: str = "lambda_handler",
) -> Dict:
    idempotency_key_hash = f"{function_name}.{handler_name}#{hash_idempotency_key(data)}"
    return {
        "ConditionExpression": (
            "attribute_not_exists(#id) OR #expiry < :now OR "
            "(#status = :inprogress AND attribute_exists(#in_progress_expiry) AND #in_progress_expiry < :now_in_millis)"
        ),
        "ExpressionAttributeNames": {
            "#id": "id",
            "#expiry": "expiration",
            "#status": "status",
            "#in_progress_expiry": "in_progress_expiration",
        },
        "ExpressionAttributeValues": {":now": stub.ANY, ":now_in_millis": stub.ANY, ":inprogress": "INPROGRESS"},
        "Item": {
            "expiration": stub.ANY,
            "id": idempotency_key_hash,
            "status": "INPROGRESS",
            "in_progress_expiration": stub.ANY,
        },
        "TableName": "TEST_TABLE",
    }


def build_idempotency_update_item_stub(
    data: Dict,
    handler_response: Dict,
    function_name: str = "test-func",
    handler_name: str = "lambda_handler",
) -> Dict:
    idempotency_key_hash = f"{function_name}.{handler_name}#{hash_idempotency_key(data)}"
    serialized_lambda_response = json_serialize(handler_response)
    return {
        "ExpressionAttributeNames": {
            "#expiry": "expiration",
            "#response_data": "data",
            "#status": "status",
        },
        "ExpressionAttributeValues": {
            ":expiry": stub.ANY,
            ":response_data": serialized_lambda_response,
            ":status": "COMPLETED",
        },
        "Key": {"id": idempotency_key_hash},
        "TableName": "TEST_TABLE",
        "UpdateExpression": "SET #response_data = :response_data, " "#expiry = :expiry, #status = :status",
    }
