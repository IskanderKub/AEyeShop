from fastapi import FastAPI
from api.database import engine, Base
from api.routers import search, tracker


app = FastAPI()
app.include_router(search.router)
app.include_router(tracker.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"status": "API is running"}

