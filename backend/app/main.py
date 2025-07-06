#main.py
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Trade Optimizer API")

app.include_router(router)

