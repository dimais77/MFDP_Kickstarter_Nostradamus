from models.prediction import PredictionHistory
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)


def create_prediction(user_id: int, model_id: int, input_data: str,
                      output_data: str, credits_used: float,
                      session) -> PredictionHistory:
    prediction = PredictionHistory(
        user_id=user_id,
        model_id=model_id,
        input_data=input_data,
        output_data=output_data,
        credits_used=credits_used
    )
    session.add(prediction)
    session.commit()
    session.refresh(prediction)
    return prediction


def get_prediction_history(user_id: int, session) -> Optional[
    PredictionHistory]:
    prediction_history = session.query(PredictionHistory).filter(
        PredictionHistory.user_id == user_id).all()
    return prediction_history
