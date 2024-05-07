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
    card_number: str  # Use str to handle numbers starting with zero
    expiration_date: str
    cvs: int
    amount: float

@router.post("/deposit")
def deposit(deposit_info: Wallet):
    """Process a deposit after verifying the credit card details and user authentication."""
    # Validate the credit card number using Luhn algorithm
    def luhn_check(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10 == 0

    if not luhn_check(deposit_info.card_number):
        raise HTTPException(status_code=400, detail="Invalid credit card number.")

    # Check expiration date
    exp_date = datetime.strptime(deposit_info.expiration_date, "%m/%y")
    if exp_date < datetime.now():
        raise HTTPException(status_code=400, detail="Credit card is expired.")

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
    # Validate the credit card number using Luhn algorithm
    def luhn_check(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10 == 0

    if not luhn_check(withdraw_info.card_number):
        raise HTTPException(status_code=400, detail="Invalid credit card number.")

    # Check expiration date
    exp_date = datetime.strptime(withdraw_info.expiration_date, "%m/%y")
    if exp_date < datetime.now():
        raise HTTPException(status_code=400, detail="Credit card is expired.")

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
        current_wallet_balance = update_wallet = sqlalchemy.text(
            "SELECT wallet FROM users users WHERE username = :username",{"username": withdraw_info.username}
        )  # Assuming wallet balance is the second column in the SELECT
        if withdraw_info.amount > current_wallet_balance:
            raise HTTPException(status_code=400, detail="Insufficient funds.")

        # Update user's wallet balance
        update_wallet = sqlalchemy.text(
            "UPDATE users SET wallet = wallet - :amount WHERE username = :username"
        )
        connection.execute(update_wallet, {
            'amount': withdraw_info.amount,
            'username': withdraw_info.username
        })

    return {"message": "Withdrawal successful!"}