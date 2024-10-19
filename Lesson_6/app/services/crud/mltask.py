from models.mltask import MLTask
from services.crud import mlmodel as ModelService
from services.crud import prediction as PredictionService
from typing import Optional, Any
from fastapi import HTTPException
from models.project_params import ProjectParams
from pydantic import BaseModel
import logging
import json
import pandas as pd
from pathlib import Path
import joblib

logging.basicConfig(level=logging.INFO)


def json_serializable(data: Any) -> Any:
    if isinstance(data, BaseModel):
        return data.dict()
    elif isinstance(data, list):
        return [json_serializable(item) for item in data]
    elif isinstance(data, dict):
        return {key: json_serializable(value) for key, value in data.items()}
    else:
        return data


def create_task(task: MLTask, session) -> MLTask:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update_task_status(task: MLTask, status: str, session) -> None:
    task.status = status
    session.commit()
    session.refresh(task)


def get_task_by_id(task_id: int, session) -> Optional[MLTask]:
    task = session.query(MLTask).filter(MLTask.task_id == task_id).first()
    return task


def get_prediction(task: MLTask, session) -> str:
    model = ModelService.get_model_by_id(task.model_id, session)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    model_path = Path(__file__).parent.parent.parent / 'data' / 'lr_model.joblib'
    if not model_path.is_file():
        raise FileNotFoundError(f"Model file not found at {model_path}")
    mlmodel = joblib.load(model_path)
    logging.info(f"Model loaded {model_path}")
    try:
        input_data_dict = json.loads(task.input_data)
        input_data_obj = ProjectParams(**input_data_dict)
        input_data_df = pd.DataFrame([input_data_obj.to_list()],
                                     columns=input_data_dict.keys())

        logging.info("Model received  params for prediction.")

        prediction = mlmodel.predict(input_data_df)
        predicted_quality = int(prediction[0])
        if predicted_quality == 1:
            output_data = 'Success'
        else:
            output_data = 'Failure'

        logging.info(f"Predicted: '{output_data}'")

        output_data = json.dumps({"predicted": output_data})
        task.output_data = output_data
        update_task_status(task, 'completed', session)

        PredictionService.create_prediction(
            user_id=task.user_id,
            model_id=task.model_id,
            input_data=task.input_data,
            output_data=task.output_data,
            credits_used=50,
            session=session
        )

        return output_data
    except Exception as e:
        update_task_status(task, 'failed', session)
        raise HTTPException(status_code=500,
                            detail=f"Prediction failed: {str(e)}")
