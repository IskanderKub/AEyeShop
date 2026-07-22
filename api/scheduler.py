import asyncio
import httpx
from sqlalchemy import select
from api.database import async_session
from api.models import PriceTracker
from api.ebay import get_item_details

async def check_prices(bot): # function to send notification
    async with async_session() as db: #open session to DB as get_db in FastAPI

        #get all tracked items from database price_tracker
        result = await db.execute(select(PriceTracker)) 
        trackers = result.scalars().all()

        for tracker in trackers:
            #get current price from eBay
            details = await get_item_details(tracker.item_id)
            current_price = float(details.get("price", "0").split()[0])

            if current_price <= tracker.target_price:
                # send notification to user
                await bot.send_message(
                    tracker.user_id,
                    f"🔔 Price Alert!\n\n"
                    f"<b>{tracker.title}</b>\n"
                    f"💰 Now: ${current_price}\n"
                    f"🎯 Your target: ${tracker.target_price}\n\n"
                    f"<a href='{tracker.url}'>Open on eBay</a>",
                    parse_mode="HTML"
                )
                # remove from tracker after notification
                await db.delete(tracker)
                await db.commit()

async def start_scheduler(bot):
    while True:
        await check_prices(bot) # check prices
        await asyncio.sleep(3600) # wait 1 hour before next check
