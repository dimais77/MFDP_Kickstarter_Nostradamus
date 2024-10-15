from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.home import home_router
from routes.user import user_router
from routes.transaction import transaction_router
from routes.mltask import mltask_router
from routes.mlmodel import mlmodel_router
from routes.prediction import prediction_router
from database.database import init_db
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(home_router)
app.include_router(user_router, prefix="/user")
app.include_router(mlmodel_router, prefix="/model")
app.include_router(transaction_router, prefix="/transaction")
app.include_router(mltask_router, prefix="/task")
app.include_router(prediction_router, prefix="/prediction")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


if __name__ == "__main__":
    uvicorn.run('api:app', host='0.0.0.0', port=8080, reload=True)
