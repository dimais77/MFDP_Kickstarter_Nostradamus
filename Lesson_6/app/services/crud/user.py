from models.user import User, SignIn
from typing import Optional
import hashlib
import logging

logging.basicConfig(level=logging.INFO)


def create_user(new_user: User, session) -> User:
    session.add(new_user)
    session.commit()
    session.refresh(new_user)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(self, password: str) -> bool:
    return self.password == self.hash_password(password)


def get_all_users(session) -> list[User]:
    users = session.query(User).all()
    return users


def get_user_by_id(user_id: int, session) -> Optional[User]:
    user = session.get(User, user_id)
    return user


def get_user_by_username(username: str, session) -> Optional[User]:
    user = session.query(User).filter(User.username == username).first()
    return user


def get_user_by_email(email: str, session) -> Optional[User]:
    user = session.query(User).filter(User.email == email).first()
    return user


from models.transaction import TransactionHistory
from services.crud import transaction as TransactionService


def add_balance(user: User, amount: float, session) -> float:
    user.balance += amount
    transaction = TransactionHistory(user_id=user.user_id,
                                     transaction_type="add", amount=amount)
    TransactionService.create_transaction(transaction, session)
    return user.balance


def deduct_balance(user: User, amount: float, session) -> float:
    if user.balance >= amount:
        user.balance -= amount
        transaction = TransactionHistory(user_id=user.user_id,
                                         transaction_type="deduct",
                                         amount=amount)
        TransactionService.create_transaction(transaction, session)
        return user.balance
    else:
        raise ValueError("Insufficient balance")


def update_balance(user: User, amount: float, operation: str,
                   session) -> float:
    if operation == 'add':
        add_balance(user, amount, session)
    elif operation == 'deduct':
        deduct_balance(user, amount, session)
    else:
        raise ValueError("Invalid operation")
