from sqlalchemy import BigInteger, Integer, Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) ## create id user with primary key
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now()) ## date of creation of user
    searches: Mapped[list["SearchHistory"]] = relationship(back_populates="user") ## create relationship with SearchHistory table

class SearchHistory(Base):
    __tablename__ = "search_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) ## create id search history with primary key
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    search_query: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now()) ## date of creation of search history
    user: Mapped["User"] = relationship(back_populates="searches") ## create relationship with User table
    search_type: Mapped[str] = mapped_column(String(20), server_default="normal")
    
class PriceTracker(Base):
    __tablename__ = "price_tracker"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) #added to track items by id
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))  # who is tracking
    item_id: Mapped[str] = mapped_column(String(100))  # eBay item id
    title: Mapped[str] = mapped_column(String(255))  # item title
    target_price: Mapped[float] = mapped_column(Float)  # price user wants to be notified at
    current_price: Mapped[float] = mapped_column(Float)  # current price on eBay
    url: Mapped[str] = mapped_column(String(500))  # link to item
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())