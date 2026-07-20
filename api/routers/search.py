from api.ebay import search_ebay
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


   items = await search_ebay(data.query) # real search on eBay

   return {
     "status": "ok",
     "query": data.query,
     "items": items
    } 

@router.get("/history/{user_id}") # add endpoint to create history function
async def get_history(user_id: int, db: AsyncSession = Depends(get_db)): # find history using user_id and pgsql
   result = await db.execute( # send request in DB
      select(SearchHistory) #search in search_history table (SELECT * FROM search_history;)
      .where(SearchHistory.user_id == user_id) #filter by user_id - take request only from this user
      .order_by(SearchHistory.created_at.desc())  #Sort by data - new requests from the top (.deck() means from new to old requests)
      .limit(10) # 10 last requests max, to don't load whole history

   )
   history = result.scalars().all() # get all results as list

   return { # return history to bot
      "history": [
         {
          "query": h.search_query, #search query text
          "date": str(h.created_at)#date of search
          }
         for h in history # loop through each history record
      ]
   }