from fastapi import APIRouter, HTTPException
from Backend.models.user import UserSignup, UserLogin
from Backend.utils.hashing import hash_password, verify_password
from Backend.database.user_crud import get_user_by_email, create_user

router = APIRouter(prefix="/api/auth")

@router.post("/signup")
def signup(user: UserSignup):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    create_user({
        "name": user.name, 
        "email": user.email, 
        "password": hashed_pw,
        "role": "user"  # Default role
    })
    return {"message": "Signup successful"}

@router.post("/login")
def login(user: UserLogin):
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "message": "Login successful",
        "name": db_user.get("name"),
        "email": db_user.get("email"),
        "role": db_user.get("role", "user")
    }
