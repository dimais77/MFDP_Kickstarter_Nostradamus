from fastapi import APIRouter
import logging

logging.basicConfig(level=logging.INFO)

home_router = APIRouter()


@home_router.get('/', tags=['Home'])
async def index() -> str:
    return "Добро пожаловать в наш сервис «Кикстартерный Нострадамус»"
