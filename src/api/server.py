from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import carts, admin, listings, portfolio, users, wallet, stats,vendor_information as vendor
import json
import logging
from starlette.middleware.cors import CORSMiddleware

description = """
Buy and sell shoes here
"""

app = FastAPI(
    title="Ecommerce shoes",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Tarj Mecwan",
        "email": "tmecwan@calpoly.edu",
    },
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(wallet.router)
app.include_router(carts.router)
app.include_router(listings.router)
app.include_router(portfolio.router)
app.include_router(users.router)
app.include_router(stats.router)
app.include_router(admin.router)
app.include_router(vendor.router)

@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to the Ecommerce Site."}
