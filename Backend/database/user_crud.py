from Backend.database.connect import users_collection

def get_user_by_email(email: str):
    return users_collection.find_one({"email": email})

def create_user(user_data: dict):
    users_collection.insert_one(user_data)