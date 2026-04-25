from fastapi import APIRouter, Depends, HTTPException
from app.schemas.rank import RankRequest, RankResponse
from app.services.scorer import OnetScorer

router = APIRouter(prefix="/v1", tags=["rank"])

scorer = OnetScorer()

@router.post("/rank", response_model=RankResponse)
def rank_resumes(request: RankRequest):
    try:
        result = scorer.score_batch(request)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))

