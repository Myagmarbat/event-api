from fastapi import FastAPI
from app.routes import events, health
app = FastAPI()
app.include_router(health.router)
app.include_router(events.router)


