from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"],
    dependencies=[Depends(auth.get_api_key)],
)

class Wallet(BaseModel):
    username: str
    auth_token: str
    amount: float

@router.post("/deposit")
def deposit(deposit_info: Wallet):
    """Process a deposit after verifying the credit card details and user authentication."""

    # Ensure the deposit amount is not negative
    if deposit_info.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive.")

    # Authenticate user and token
    with db.engine.begin() as connection:
        auth_token = connection.execute(
            sqlalchemy.text("SELECT auth_token FROM users WHERE username = :username"),
            {'username': deposit_info.username}
        ).fetchone()

        if str(deposit_info.auth_token) != str(auth_token[0]):
            raise HTTPException(status_code=401, detail="Unauthorized access.")

        # Update user's wallet balance
        update_wallet = sqlalchemy.text(
            "UPDATE users SET wallet = wallet + :amount WHERE username = :username"
        )
        connection.execute(update_wallet, {
            'amount': deposit_info.amount,
            'username': deposit_info.username
        })

    return {"message": "Deposit successful!"}

@router.post("/withdraw")
def withdraw(withdraw_info: Wallet):
    """Process a wallet after verifying the credit card details and user authentication."""

    # Ensure the withdrawal amount is not negative
    if withdraw_info.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdraw amount must be positive.")

    with db.engine.begin() as connection:
        # Authenticate user and token
        auth_token = connection.execute(
            sqlalchemy.text("SELECT auth_token, wallet FROM users WHERE username = :username"),
            {'username': withdraw_info.username}
        ).fetchone()

        if auth_token is None or str(withdraw_info.auth_token) != str(auth_token[0]):
            raise HTTPException(status_code=401, detail="Unauthorized access.")

        # Check if the wallet balance is sufficient
        current_wallet_balance = connection.execute(
            sqlalchemy.text("""
                SELECT wallet FROM users WHERE username = :username
            """),
            {"username": withdraw_info.username}
        ).fetchone()

        if withdraw_info.amount > current_wallet_balance.wallet:
            raise HTTPException(status_code=400, detail="Insufficient funds.")

        # Update user's wallet balance
        connection.execute(
            sqlalchemy.text("""
                UPDATE users SET wallet = wallet - :amount WHERE username = :username
            """),
            {
                'amount': withdraw_info.amount,
                'username': withdraw_info.username
            })

    return {"message": "Withdrawal successful!"}