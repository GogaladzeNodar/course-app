import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_LOGGING = {
    "HOST": os.getenv("MONGO_HOST", "mongo_logging"),
    "PORT": int(os.getenv("MONGO_PORT", 27017)),
    "DB_NAME": os.getenv("MONGO_DB_NAME", "logs"),
    "USER": os.getenv("MONGO_LOG_USER", "logger"),
    "PASSWORD": os.getenv("MONGO_LOG_PASSWORD", "logger_pass"),
    "COLLECTION": "app_logs",
}

client = MongoClient(
    host=MONGO_LOGGING["HOST"],
    port=MONGO_LOGGING["PORT"],
    username=MONGO_LOGGING["USER"],
    password=MONGO_LOGGING["PASSWORD"],
    authSource=MONGO_LOGGING["DB_NAME"],
)

collection = client[MONGO_LOGGING["DB_NAME"]][MONGO_LOGGING["COLLECTION"]]


def mongo_sink(message):
    record = message.record
    doc = {
        "level": record["level"].name,
        "message": record["message"],
        "event": record["extra"].get("event"),
        "user_id": record["extra"].get("user_id"),
        "request_id": record["extra"].get("request_id"),
        "module": record["module"],
        "view": record["extra"].get("view"),
        "function": record["extra"].get("function"),
        "duration_ms": record["extra"].get("duration_ms"), 
        "time": record["time"].isoformat(),
    }
    collection.insert_one(doc)