import os
import time
import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def increment_counter(key = "web_counter"):
    timestamp = int(time.time())
    try:
        response = table.update_item(
            Key={"id": key, "updated_at": timestamp},
            UpdateExpression="SET visits = if_not_exists(visits, :start) + :inc",
            ExpressionAttributeValues={":inc": 1, ":start": 0},
            ReturnValues="UPDATED_NEW",
        )
        return {"status": "success", "visits": response["Attributes"]["visits"]}
    except Exception as e:
        print(f"Error incrementing counter: {str(e)}")
        return {"status": "error", "message": "Could not increment counter"}


def handler(event=None, _context=None):
    visit_count = increment_counter()

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"visits": visit_count, "timestamp": int(time.time())}),
    }
