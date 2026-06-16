from fastapi import APIRouter
from pydantic import BaseModel

from workers.token_traders import analyze_token_traders


router = APIRouter(
    prefix="/traders"
)



class TraderRequest(BaseModel):

    token:str
    sort_by:str="entry_mc"




@router.post("/analyze")
def analyze(
    req:TraderRequest
):

    return analyze_token_traders(
        req.token,
        req.sort_by
    )