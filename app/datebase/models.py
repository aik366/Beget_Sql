from config import DB_URL
from sqlalchemy import String, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url=DB_URL, echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger)
    full_name = mapped_column(String(50))
    data = mapped_column(String(20))


class Birthday(Base):
    __tablename__ = "birthday"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(ForeignKey("users.tg_id"))
    surname = mapped_column(String(20))
    name = mapped_column(String(20))
    date = mapped_column(String(20))
    delta_time = mapped_column(Integer)
    age = mapped_column(Integer)


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(ForeignKey("users.tg_id"))
    note_name: Mapped[str] = mapped_column(String(20))
    note_type: Mapped[str] = mapped_column(String(20))
    note_text: Mapped[str] = mapped_column(String())
    file_id: Mapped[str] = mapped_column(String(512))
    note_date: Mapped[str] = mapped_column(String(20))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    import asyncio

    asyncio.run(async_main())
