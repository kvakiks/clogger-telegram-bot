from sqlalchemy import Integer, BigInteger, String, Date
from sqlalchemy import func, MetaData, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

from datetime import date


metadata = MetaData(
    naming_convention={
        'pk': 'pk_%(table_name)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'ix': 'ix_%(column_0_label)s'
    }
)

class Base(AsyncAttrs, DeclarativeBase):
    metadata = metadata


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

class Consumption(Base):
    __tablename__ = 'consumptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True) 

    consumer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id'), ondelete='CASCADE')

    category: Mapped[str] = mapped_column(String(30), nullable=False)
    spent: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[date] = mapped_column(Date, server_default=func.current_date()) # Сделать перевод даты на MSK при запросах

    user: Mapped['User'] = relationship()

    __table_args__ = (
        Index(None, consumer_id, created_at),
    )
