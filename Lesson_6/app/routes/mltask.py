from fastapi import APIRouter, HTTPException, Depends
from models.mltask import MLTask
from models.wineparams import WineParams
from services.crud import mltask as MLTaskService
from services.crud import mlmodel as MLModelService
from services.crud import user as UserService
from database.database import get_session
import json
import logging

logging.basicConfig(level=logging.INFO)

mltask_router = APIRouter(tags=['MLTasks'])

CREDITS_USED = 50


@mltask_router.get('/{task_id}', response_model=MLTask)
async def get_task_by_id(task_id: int, session=Depends(get_session)):
    task = MLTaskService.get_task_by_id(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@mltask_router.post('/newtask')
async def create_task(user_id: int, model_id: int, input_data: WineParams,
                      session=Depends(get_session)):
    mlmodel = MLModelService.get_model_by_id(model_id, session)
    logging.info(f"create_task ---- mlmodel==={mlmodel}")
    if mlmodel is None:
        raise HTTPException(status_code=404, detail="Model not found")

    user = UserService.get_user_by_id(user_id, session)
    logging.info(f"create_task ---- user==={user}")
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.balance < CREDITS_USED:
        raise HTTPException(status_code=403,
                            detail="Insufficient balance to create task")

    input_data_dict = input_data.dict()
    logging.info(f"create_task ---- input_data_dict==={input_data_dict}")
    input_data_json = json.dumps(input_data_dict)
    logging.info(f"create_task ---- input_data_json==={input_data_json}")

    task = MLTask(user_id=user_id, model_id=model_id,
                  input_data=input_data_json)
    created_task = MLTaskService.create_task(task, session)
    logging.info(f"create_task ---- created_task==={created_task.task_id}")

    return created_task


@mltask_router.get('/prediction/{task_id}', response_model=MLTask)
async def get_prediction(task_id: int, session=Depends(get_session)):
    task = MLTaskService.get_task_by_id(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "completed":
        output_data = MLTaskService.get_prediction(task, session)

        user = UserService.get_user_by_id(task.user_id, session)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user.balance < CREDITS_USED:
            raise HTTPException(status_code=403,
                                detail="Insufficient balance to get prediction")

        UserService.update_balance(user, amount=CREDITS_USED,
                                   operation='deduct', session=session)

        task.output_data = output_data
        task.status = "completed"
        session.commit()
        session.refresh(task)

    return task
