from pymongo import MongoClient
import os

mongodb_client = MongoClient(os.environ['MONGODB_URL'], serverSelectionTimeoutMS=5000)
mongodb_db = mongodb_client[os.environ['MONGODB_DATABASE']]