from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.database import get_db
from api.models import PriceTracker
from api.ebay import get_item_details
from pydantic import BaseModel

# Scheme of request and router
class TrackRequest(BaseModel):
    user_id: int
    item_id: str
    target_price: float

router = APIRouter(prefix="/tracker", tags=["tracker"])

# add endpoint /add

@router.post("/add")
async def add_tracker(data: TrackRequest, db: AsyncSession = Depends(get_db)):
    #get current price from eBay
    details = await get_item_details(data.item_id) # Take info about item form Ebay
    current_price = float(details.get("price", "0").split()[0]) #  "269.99 USD" cut to "269.99" and turn in to float

    # save to price_tracker table into DB
    tracker = PriceTracker(
        user_id=data.user_id,
        item_id=data.item_id,
        title=details.get("title", "Unknown"),
        target_price=data.target_price,
        current_price=current_price,
        url=details.get("url", "")
    )

    db.add(tracker)
    await db.commit()

    return {"status": "ok", "title": details.get("title"), "target_price": data.target_price} # send bot aprovement