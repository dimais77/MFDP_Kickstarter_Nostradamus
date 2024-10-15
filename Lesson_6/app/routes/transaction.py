from fastapi import APIRouter, HTTPException, Depends
from models.transaction import TransactionHistory
from services.crud import transaction as TransactionService
from database.database import get_session
import logging

logging.basicConfig(level=logging.INFO)

transaction_router = APIRouter(tags=['Transactions'])

@transaction_router.get("/transactions_history")
async def get_all_transaction_history(session = Depends(get_session)):
    transactions = TransactionService.get_all_transaction_history(session)
    return transactions


@transaction_router.get("/transactions_history/{user_id}")
async def get_transaction_history(user_id: int, session = Depends(get_session)):
    transaction_history = session.query(TransactionHistory).filter(
        TransactionHistory.user_id == user_id).all()
    if not transaction_history:
        raise HTTPException(status_code=404,
                            detail="No transactions found for user")
    return transaction_history
