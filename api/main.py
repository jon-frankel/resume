def handler(event=None, context=None):
    return {
        "statusCode": 200,
        "content-type":"application/json",
        "body": {
            "message": "Hello, World!",
            "event": event,
            "context": context
        }
    }
