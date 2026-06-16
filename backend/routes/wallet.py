from fastapi import APIRouter
from pydantic import BaseModel

from backend.workers.wallet_checker import analyze_token


router = APIRouter(
    prefix="/wallet",
    tags=["wallet"]
)


class TokenRequest(BaseModel):
    token: str



@router.post("/analyze")
async def analyze(
    req: TokenRequest
):

    result = await analyze_token(
        req.token
    )

    return result