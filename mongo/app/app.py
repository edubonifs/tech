from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

@app.route('/')
def show_mongodb_contents():
    # Retrieve MongoDB credentials from environment variables
    mongo_user = os.getenv('MONGO_USER')
    mongo_pass = os.getenv('MONGO_PASS')
    mongo_host = os.getenv('MONGO_HOST')
    mongo_port = os.getenv('MONGO_PORT', '27017')
    mongo_db_name = os.getenv('MONGO_DB_NAME')

    # Create a MongoDB client
    mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/"
    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]

    # Assuming a collection named 'testcollection' exists
    collection = db.testcollection
    documents = list(collection.find({}, {'_id': False}))  # Excluding _id from results

    return jsonify(documents)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

