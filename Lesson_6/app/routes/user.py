from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.database import get_session
from models.user import User, TokenResponse, GetUserResponse
from services.crud import user as UserService
import logging

logging.basicConfig(level=logging.INFO)

user_router = APIRouter(tags=['User'])

hash_password = HashPassword()


@user_router.post('/signup')
async def signup(user: User, session=Depends(get_session)) -> dict:
    user_exist = UserService.get_user_by_email(user.email, session)
    if user_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User with supplied email already exists")

    hashed_password = hash_password.create_hash(user.password)
    user.password = hashed_password
    UserService.create_user(user, session)
    return {"message": "User successfully registered!"}


@user_router.post('/signin', response_model=TokenResponse)
async def signin(user: OAuth2PasswordRequestForm = Depends(),
                 session=Depends(get_session)):
    user_exist = UserService.get_user_by_username(user.username, session)
    if user_exist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User does not exist")
    if hash_password.verify_hash(user.password, user_exist.password):
        access_token = create_access_token(user_exist.username)
        logging.info(f"access_token===routes==={access_token}")
        username = user_exist.username
        user_id = user_exist.user_id
        logging.info(f"username===routes==={username}")
        return {"access_token": access_token, "token_type": "Bearer",
                "user_id": user_id}
        logging.info(f"user_id===routes==={user_id}")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )


@user_router.get('/users', response_model=list[User])
async def get_all_users(session=Depends(get_session)) -> list[User]:
    return UserService.get_all_users(session)


@user_router.get('/user', response_model=GetUserResponse)
async def get_user_by_username(username: str, session=Depends(
    get_session)) -> GetUserResponse:
    user = UserService.get_user_by_username(username, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    return GetUserResponse(id=user.user_id, username=user.username,
                           email=user.email, balance=user.balance,
                           created_at=user.created_at)


@user_router.get('/balance/{user_id}')
async def get_balance(user_id: int, session=Depends(get_session)):
    user = UserService.get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return {"balance": user.balance}


@user_router.post('/balance/add/{user_id}')
async def add_balance(user_id: int, amount: float,
                      session=Depends(get_session)):
    user = UserService.get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    UserService.update_balance(user, amount=amount, operation='add',
                               session=session)
    session.commit()
    return {"message": "Balance added successfully"}


@user_router.post('/balance/deduct/{user_id}')
async def deduct_balance(user_id: int, amount: float,
                         session=Depends(get_session)):
    user = UserService.get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    UserService.update_balance(user, amount=amount, operation='deduct',
                               session=session)
    session.commit()
    return {"message": "Balance deduct successfully"}
