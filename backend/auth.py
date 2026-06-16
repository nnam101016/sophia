from fastapi import APIRouter
from passlib.context import CryptContext
import uuid


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


pwd = CryptContext(
    schemes=["bcrypt"]
)


users = {}


@router.post("/register")
def register(username:str, password:str):

    if username in users:
        return {
            "error":"exists"
        }


    users[username] = {
        "id": str(uuid.uuid4()),
        "password": pwd.hash(password)
    }


    return {
        "success":True
    }



@router.post("/login")
def login(username:str,password:str):

    user = users.get(username)

    if not user:
        return {
            "error":"invalid"
        }


    if not pwd.verify(
        password,
        user["password"]
    ):
        return {
            "error":"invalid"
        }


    return {
        "token":"demo-token",
        "user":username
    }