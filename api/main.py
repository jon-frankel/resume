import os
import time
import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
timestamp = int(time.time())


def increment_counter(pk ="web_counter"):
    try:
        response = table.update_item(
            Key={"id": pk},
            UpdateExpression="SET visits = if_not_exists(visits, :start) + :inc, updated_at = :timestamp",
            ExpressionAttributeValues={":inc": 1, ":start": 0, ":timestamp": timestamp},
            ReturnValues="UPDATED_NEW",
        )
        return {
            "status": "success",
            "visits": f"{response["Attributes"]["visits"]}",
            "timestamp": timestamp,
        }
    except Exception as e:
        print(f"Error incrementing counter: {str(e)}")
        return {
            "status": "error",
            "message": "Could not increment counter",
            "visits": None,
            "timestamp": timestamp,
        }


def handler(event=None, _context=None):
    method = event["requestContext"]["http"]["method"]
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"status": "success"}),
        }

    response_body = increment_counter()

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(response_body),
    }
