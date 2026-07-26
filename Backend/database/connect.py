from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["college_chatbot"]

users_collection = db["users"]
documents_collection = db["documents"]
chunks_collection = db["chunks"]