from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.database import get_db
from api.models import User, SearchHistory
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    user_id: int
    username: str | None = None
    first_name: str = "User"


## Search router to handle search requests and store them in the database
router = APIRouter(prefix="/search", tags=["search"])

@router.post("/") ## create endpoint witch take POST request with /search/
async def search(data: SearchRequest, db: AsyncSession = Depends(get_db)): ## take info about user and search from request and session for database 
   result = await db.execute(select(User).where(User.id == data.user_id)) ## check if user from request exist in database
   user = result.scalar_one_or_none() ## if user exist in database, return user object, else return None

   if not user: ## if user not exist in database, create new user
    user = User(
       id = data.user_id,
       username = data.username,
       first_name = data.first_name
    )
    db.add(user) ## add new user to database

   history = SearchHistory( ## Save search history to database
      user_id=data.user_id,
      search_query=data.query
    )
   db.add(history) ## add search history to database

   await db.commit() ## save all changes to database

   return {
    "status": "ok",
    "query": data.query,
    "items": [
        {"title": f"{data.query} - Option 1", "price": "$100.00", "condition": "New", "url": "https://ebay.com/item1"},
        {"title": f"{data.query} - Option 2", "price": "$85.00", "condition": "Used - Like New", "url": "https://ebay.com/item2"},
        {"title": f"{data.query} - Option 3", "price": "$75.00", "condition": "Used - Good", "url": "https://ebay.com/item3"},
        {"title": f"{data.query} - Option 4", "price": "$60.00", "condition": "Used", "url": "https://ebay.com/item4"},
        {"title": f"{data.query} - Option 5", "price": "$120.00", "condition": "New", "url": "https://ebay.com/item5"},
    ]
   }## return message to user that search query saved successfully

