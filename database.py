import os
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
_client = None

def get_collection():
    global _client
    if _client is None:
        _client = MongoClient(
            os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
            serverSelectionTimeoutMS=5000
        )
    return _client[os.getenv("MONGO_DB", "alerta_bairro")]["occurrences"]

def _id(value):
    if not ObjectId.is_valid(value):
        raise ValueError("Identificador inválido.")
    return ObjectId(value)

def _public(doc):
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    for key in ("created_at", "updated_at"):
        if isinstance(doc.get(key), datetime):
            doc[key] = doc[key].astimezone(timezone.utc).isoformat(timespec="seconds")
    return doc

def list_occurrences():
    cursor = get_collection().find(
        {}, {"location": 1, "description": 1, "severity": 1,
             "status": 1, "created_at": 1, "updated_at": 1}
    ).sort("created_at", -1)
    return [_public(doc) for doc in cursor]

def get_occurrence(occurrence_id):
    return _public(get_collection().find_one({"_id": _id(occurrence_id)}))

def create_occurrence(data):
    now = datetime.now(timezone.utc)
    document = dict(data, created_at=now, updated_at=now)
    return str(get_collection().insert_one(document).inserted_id)

def update_occurrence(occurrence_id, data):
    values = dict(data, updated_at=datetime.now(timezone.utc))
    result = get_collection().update_one({"_id": _id(occurrence_id)}, {"$set": values})
    return result.modified_count > 0

def delete_occurrence(occurrence_id):
    result = get_collection().delete_one({"_id": _id(occurrence_id)})
    return result.deleted_count > 0
