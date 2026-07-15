from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey, func
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

