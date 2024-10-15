from models.transaction import TransactionHistory
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)


def create_transaction(transaction: TransactionHistory,
                       session) -> TransactionHistory:
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def get_all_transaction_history(session):
    transactions = session.query(TransactionHistory).all()
    return transactions


def get_transaction_history(user_id: int, session) -> Optional[
    TransactionHistory]:
    transactions = session.query(TransactionHistory).filter(
        TransactionHistory.user_id == user_id).all()
    return transactions
