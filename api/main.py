import os
import time
import boto3

def get_dynamodb():
    return boto3.resource("dynamodb")


dynamodb = get_dynamodb()
table = dynamodb.Table(os.environ["TABLE_NAME"])


def increment_counter(pk ="web_counter"):
    timestamp = int(time.time())
    try:
        response = table.update_item(
            Key={"id": pk},
            UpdateExpression="SET visits = if_not_exists(visits, :start) + :inc, updated_at = :timestamp",
            ExpressionAttributeValues={":inc": 1, ":start": 0, ":timestamp": timestamp},
            ReturnValues="UPDATED_NEW",
        )
        return {
            "status": "success",
            "visits": int(response["Attributes"]["visits"]),
            "timestamp": timestamp,
        }
    except Exception as e:
        print(f"Error incrementing counter: {str(e)}")
        return {
            "status": "error",
            "message": "Could not increment counter",
            "visits": 0,
            "timestamp": timestamp,
        }


def handler(event=None, _context=None):
    # AWS Function URL and MiniStack handles CORS via configuration,
    # and the Invoke API returns our response payload directly.
    return increment_counter()
