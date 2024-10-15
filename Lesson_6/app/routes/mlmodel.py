from fastapi import APIRouter, HTTPException, status, Depends
from models.mlmodel import MLModel
from services.crud import mlmodel as MLModelService
from services.crud import mltask as MLTaskService
from database.database import get_session
import logging
import json

logging.basicConfig(level=logging.INFO)

mlmodel_router = APIRouter(tags=['Models'])


@mlmodel_router.post('/upload_model')
async def upload_model(mlmodel: MLModel, session=Depends(get_session)):
    created_model = MLModelService.create_mlmodel(mlmodel, session)
    return {"message": "Model uploaded successfully",
            "model_id": created_model.model_id}


@mlmodel_router.post('/predict/{model_id}')
async def predict(task_id: int, session=Depends(get_session)):
    task = MLTaskService.get_task_by_id(task_id, session)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Task not found")

    input_data = json.loads(task.input_data)

    prediction = MLModelService.make_prediction(input_data)
    return {"prediction": prediction}
