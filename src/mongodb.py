from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import src.settings as settings
from bson.objectid import ObjectId


class MongoDB(object):
    def __init__(self):
        self.client = MongoClient(settings.mongo_db_uri, server_api=ServerApi("1"))
        self.db = self.client["spreadsheet_filler"]
        self.collection = self.db["memory"]

        try:
            self.client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    def insert(self, json):
        self.collection.insert_one(json)

    def find_by_id(self, object_id):
        return self.collection.find_one({"_id": ObjectId(object_id)})
