from fastapi import FastAPI
from api.routers import search
from api.database import engine, Base

app = FastAPI()
app.include_router(search.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"status": "API is running"}

