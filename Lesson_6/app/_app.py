from pathlib import Path
import joblib
import logging
import pandas as pd
from pydantic import BaseModel
from typing import List
import json

logging.basicConfig(level=logging.INFO)

logging.info(' [*] Добро пожаловать в "Wine Quality Prediction Service" [*] ')


model_path = Path(__file__).parent / 'data' / 'lr_model.joblib'
# model_path = 'data/lr_model.joblib'
filename = 'lr_model.joblib'
# /Users/dmitriiisaev/PycharmProjects/Karpov_Courses/Kickstarter_Nostradamus/app/_app.py
# /Users/dmitriiisaev/PycharmProjects/Karpov_Courses/Kickstarter_Nostradamus/app/data/lr_model.joblib
if not model_path.is_file():
    raise FileNotFoundError(f"Model file not found at {model_path}")
logging.info(f"{model_path}")
mlmodel = joblib.load(filename)
logging.info(f"Model loaded.")


if (mlmodel is not None and hasattr(mlmodel, 'predict') and callable(
        getattr(mlmodel, 'predict'))):
    logging.info("Model ready to predict.")
else:
    logging.info("Model not ready")


class WineParams(BaseModel):
    # class ProjectParams(BaseModel):
    blurb: str
    currency: str
    goal: float
    campaign_duration: int
    started_month: int
    category_subcategory: str

    def to_list(self) -> List[float]:
        return [
            self.blurb,
            self.currency,
            self.goal,
            self.campaign_duration,
            self.started_month,
            self.category_subcategory,
        ]


payload = {
  "blurb": "Chill Magazine is a woman run, print-only literary art magazine for chillers",
  "currency": "USD",
  "goal": 3500,
  "campaign_duration": 30,
  "started_month": 7,
  "category_subcategory": "Publishing Art Books"
}
# Преобразование входных данных в модель Pydantic
wine_params = WineParams(**payload)

# Преобразование данных в список списков для предсказания
input_data = pd.DataFrame([wine_params.to_list()], columns=payload.keys())
logging.info(f"Model received wine params for prediction.")

predicted_quality = int(mlmodel.predict(input_data)[0])

if predicted_quality==1:
    output_data='Good wine!'
else:
    output_data='Bad wine...'

logging.info(f"Predicted wine quality: '{output_data}'")



def json_serializable(data):
    if isinstance(data, BaseModel):
        return data.dict()
    elif isinstance(data, list):
        return [json_serializable(item) for item in data]
    elif isinstance(data, dict):
        return {key: json_serializable(value) for key, value in data.items()}
    else:
        return data

data=payload
serializable_data = json_serializable(data)
logging.info(f"serializable_data: {serializable_data}")
body = json.dumps(serializable_data)
logging.info(f"json.dumps: {body}")


#########################################

# from database.database import init_db, engine
# from services.crud.user import *
# from services.crud.mlmodel import *
# from services.crud.transaction import *
# from models.user import User
# from models.mlmodel import MLModel
# from models.transaction import TransactionHistory
#
#
# def main():
#     """Создание демо данных для инициализации базы данных."""
#     # Создание пользователей
#     test_user_1 = User(username='Dima', email='dima@mail.ru', password='12345678', balance=100.00)
#     test_user_2 = User(username='Yura', email='yura@mail.ru', password='12345678', balance=100.00)
#     test_user_3 = User(username='Kolya', email='kolya@mail.ru', password='12345678', balance=100.00)
#
#     # Создание моделей
#     test_mlmodel_1 = MLModel(model_name='LinerRegression', version='Ver. 1.0', description='-')
#     test_mlmodel_2 = MLModel(model_name='RandomForest', version='Ver. 2.0', description='-')
#
#     # Создание транзакций
#     test_transaction_1 = TransactionHistory(user_id=1, amount=50, description='deduct balance')
#     test_transaction_2 = TransactionHistory(user_id=2, amount=50, description='deduct balance')
#     test_transaction_3 = TransactionHistory(user_id=3, amount=50, description='add balance')
#
#     # Инициализация базы данных
#     init_db()
#
#     with Session(engine) as session:
#         create_user(test_user_1, session=session)
#         create_user(test_user_2, session=session)
#         create_user(test_user_3, session=session)
#         users = get_all_users(session)
#
#     print(f"Созданы новые пользователи:")
#     for user in users:
#         print(f"{user.user_id} - {user.username} - {user.email} - {user.balance}")
#
#     with Session(engine) as session:
#         create_mlmodel(test_mlmodel_1, session=session)
#         create_mlmodel(test_mlmodel_2, session=session)
#         mlmodels = get_all_mlmodels(session)
#
#     print(f"Загружены ML-модели:")
#     for mlmodel in mlmodels:
#         print(f"{mlmodel.model_id} - {mlmodel.model_name} - {mlmodel.version}")
#
#     with Session(engine) as session:
#         create_transaction(test_transaction_1, session=session)
#         create_transaction(test_transaction_2, session=session)
#         create_transaction(test_transaction_3, session=session)
#         transactions = get_all_transactions(session)
#
#     print(f"Список транзакций:")
#     for transaction in transactions:
#         print(
#             f"Транзакция №{transaction.transaction_id} "
#             f"- пользователь(id) {transaction.user_id} "
#             f"- сумма {transaction.amount} "
#             f"- {transaction.description}")
#
#     # Обновление балансов пользователей
#     update_user_balance(user=test_user_1, amount=50.00, operation='deduct', session=session)
#     update_user_balance(user=test_user_2, amount=50.00, operation='deduct', session=session)
#     update_user_balance(user=test_user_3, amount=50.00, operation='add', session=session)
#
#     with Session(engine) as session:
#         users = get_all_users(session)
#
#     print(f"Обновлены балансы пользователей:")
#     for user in users:
#         print(f"{user.user_id} - {user.username} - {user.email} - {user.balance}")
#
#
# if __name__ == "__main__":
#     main()

########################################

# # import os
# # from sqlmodel import Session
# # from database.config import get_settings
# # from database.database import get_session
# #
# #
# # if __name__ == '__main__':
# #     test_user = User(1, 'Dima', 'dima@mail.ru', '12345678', 100.00)
# #     settings = get_settings()
# #     print(settings.DB_HOST)
# #     print(settings.DB_NAME)
# #
# #     print('Init db has been success')
# #
# #
# # import os
# # from mlmodels.user import User
# # from mlmodels.mltask import MLTask
# # from mlmodels.mlmodel import RegressionModel
# #
# #
# # def main():
# #     rabbitmq_url = os.getenv("RABBITMQ_URL")
# #     print(f"Connecting to RabbitMQ at {rabbitmq_url}")
# #
# #     test_user = User(1, 'Dima', '12345678', 'dima@mail.ru', 100.00)
# #     print(f"User {test_user.user_id} added to the database.")
# #
# #     regression_model = RegressionModel(model_id=1, name="Test Regression Model", version="1.0",
# #                                        description="A simple regression model")
# #     ml_task = MLTask(task_id=1, user_id=test_user.user_id, model=regression_model, data=[1, 2, 3],
# #                      status="pending")
# #     print(f"MLTask created for User {test_user.user_id}:")
# #     print(f"Task ID: {ml_task.task_id}")
# #     print(f"User ID: {ml_task.user_id}")
# #     print(f"Model: {ml_task.model.name}")
# #     print(f"Data: {ml_task.data}")
# #     print(f"Status: {ml_task.status}")
# #
# #
# # if __name__ == "__main__":
# #     main()
