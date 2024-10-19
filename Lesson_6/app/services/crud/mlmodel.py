from models.mlmodel import MLModel
from models.project_params import ProjectParams
from typing import Optional, Sequence
from pathlib import Path
import joblib
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    model_path = Path(__file__).parent.parent.parent / 'data' / 'lr_model.joblib'

    if not model_path.is_file():
        logger.error(f"Model file not found at {model_path}")
        raise FileNotFoundError(f"Model file not found at {model_path}")

    try:
        mlmodel = joblib.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise ValueError(f"Could not load model from {model_path}: {e}")

    if not hasattr(mlmodel, 'predict'):
        logger.error(
            f"Loaded model does not have a 'predict' method - {model_path}")
        raise ValueError(
            f"Loaded model does not have a 'predict' method - {model_path}")

    if not isinstance(payload, dict):
        logger.error(f"Expected dictionary, got {type(payload).__name__}")
        raise ValueError("Invalid input data format")

    try:
        project_params = ProjectParams(**payload)
    except TypeError as e:
        logger.error(f"Error creating ProjectParams: {e}")
        raise ValueError("Invalid input data format for ProjectParams")

    try:
        input_data = pd.DataFrame([project_params.to_list()],
                                  columns=payload.keys())
        logger.info("Input data successfully converted to DataFrame")
    except Exception as e:
        logger.error(f"Error converting input data to DataFrame: {e}")
        raise ValueError(f"Error converting input data to DataFrame: {e}")

    try:
        prediction = mlmodel.predict(input_data)
        predicted_quality = int(prediction[0])
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        raise ValueError(f"Prediction failed: {e}")

    if predicted_quality == 1:
        output_data = 'Success'
    else:
        output_data = 'Failure'

    logger.info(f"Prediction result: '{output_data}'")

    return output_data
