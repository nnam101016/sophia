from fastapi import FastAPI
from backend.routes import wallet
from backend.auth import router as auth_router
from backend.routes import traders

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()



app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(wallet.router)
app.include_router(traders.router)

@app.get("/")
def home():
    return {
        "status": "online"
    }