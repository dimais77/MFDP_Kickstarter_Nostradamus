from models.mlmodel import MLModel
from models.wineparams import WineParams
from typing import Optional, Sequence
from pathlib import Path
import joblib
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)


def create_mlmodel(mlmodel: MLModel, session) -> MLModel:
    session.add(mlmodel)
    session.commit()
    session.refresh(mlmodel)
    return mlmodel


def get_all_mlmodels(session) -> Sequence[MLModel]:
    return session.query(MLModel).all()


def get_model_by_id(model_id: int, session) -> Optional[MLModel]:
    return session.get(MLModel, model_id)


def make_prediction(payload: dict) -> str:
    model_path = Path(__file__).parent.parent.parent / 'data' / 'model.pkl'
    if not model_path.is_file():
        raise FileNotFoundError(f"Model file not found at {model_path}")
    mlmodel = joblib.load(model_path)
    logging.info(f"Model loaded {model_path}")

    if not hasattr(mlmodel, 'predict'):
        raise ValueError(
            f"Loaded model does not have a 'predict' method - {model_path}")

    if not isinstance(payload, dict):
        logging.error(f"Expected dictionary, got {type(payload).__name__}")
        raise ValueError("Invalid input data format")

    try:
        wine_params = WineParams(**payload)
    except TypeError as e:
        logging.error(f"Error creating WineParams: {e}")
        raise ValueError("Invalid input data format")

    # Преобразование данных в DataFrame для предсказания
    input_data = pd.DataFrame([wine_params.to_list()], columns=payload.keys())

    # Выполнение предсказания
    prediction = mlmodel.predict(input_data)
    predicted_quality = int(prediction[0])

    if predicted_quality == 1:
        output_data = 'Good wine'
    else:
        output_data = 'Bad wine'

    logging.info(f"Predicted wine quality: '{output_data}'")

    return output_data
