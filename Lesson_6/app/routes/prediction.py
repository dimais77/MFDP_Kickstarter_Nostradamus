from fastapi import APIRouter, HTTPException, Depends
from models.prediction import PredictionHistory
from database.database import get_session
import logging

logging.basicConfig(level=logging.INFO)

prediction_router = APIRouter(tags=['Predictions'])


@prediction_router.get("/{user_id}")
def get_prediction_history(user_id: int,
                           session=Depends(get_session)):
    prediction_history = session.query(PredictionHistory).filter(
        PredictionHistory.user_id == user_id).all()
    if not prediction_history:
        raise HTTPException(status_code=404,
                            detail="No predictions found for user")
    return prediction_history
