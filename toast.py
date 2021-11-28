from pymongo.mongo_client import MongoClient


mongodb_client = MongoClient('mongodb+srv://goat_seo_backend:9Cq2Wc856X403nDy@db-mongodb-sfo3-69623-seo-1c4a5e12.mongo.ondigitalocean.com/goat_seo?authSource=admin&replicaSet=db-mongodb-sfo3-69623-seo&tls=true&tlsCAFile=mongodb-ca-certificate.crt', serverSelectionTimeoutMS=5000)
mongodb_db = mongodb_client['goat_seo']

import pprint

