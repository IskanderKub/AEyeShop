from api.ebay import search_ebay, get_item_details
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
    offset: int = 0 


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

   # add skip queries to don't let buttons be in search
   SKIP_QUERIES = {"➕ More results", "🏛 History", "🗑 Delete All", "🗑 Delete specific", "🧮 Delete specific", "⬅️ Menu", "🔄 Search again", "🔎 Search"}

   if data.query not in SKIP_QUERIES:
      history = SearchHistory( ## Save search history to database
         user_id=data.user_id,
         search_query=data.query
      )
      db.add(history) ## add search history to database
      await db.commit() ## save all changes to database

   try:
      items = await search_ebay(data.query, data.offset) # real search on eBay, and offset
      #eBay returned 100 items by request "thinkpad"

      #offset=0  → show items 1-5
      #offset=5  → show items 6-10
      #offset=10 → show items 11-15

   except Exception as e:
      print(f"eBay search error: {e}")
      items= []
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

###Details button

@router.get("/item/{item_id}") # endpoint ot get item details by item_id
async def get_item(item_id: str):
   try:
      details = await get_item_details(item_id)# get details from eBay
      return details
   except Exception as e:
      return {"error": str(e)}


# Delete all history for user
@router.delete("/history/{user_id}")
async def delete_all_history(user_id: int, db: AsyncSession = Depends(get_db)): # DELETE endpoint - take user_id from URL and delete all history

   from sqlalchemy import delete
   await db.execute(delete(SearchHistory).where(SearchHistory.user_id == user_id))
   await db.commit() # run SQL DELETE FROM search_history WHERE user_id = ... and save changes.

   return {"message": "History cleared"} # send bot conformation

# Deleter specific item from history by number

@router.delete("/history/{user_id}/{number}")
async def delete_specific_history(user_id: int, number: int, db: AsyncSession = Depends(get_db)): # second DELETE endpoint — take user_id and number (umber in note that we want to delete).

   result = await db.execute(
      select(SearchHistory)
      .where(SearchHistory.user_id == user_id)
      .order_by(SearchHistory.created_at.desc())
      .limit(10)
   )
   history = result.scalars().all() # Take last 10 requests user — same list that was in History logic

   if number < 1 or number > len(history):
      return {"message": f"Invalid number. Enter between 1 and {len(history)}."}# Confirm that number validated — not less then 1 and not more then quantity notes.

   item = history[number -1]
   await db.delete(item)
   await db.commit()
   return {"message": f"Deleted: {item.search_query}"} # Take notes from number (minus 1 cause list from zero), delete and return what exactly was deleted.