from sqlalchemy import create_engine, Integer, String, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import Optional

engine = create_engine() # Вставить базу

metadata = MetaData(
    naming_convention={
        'pk': '',        # Закончить именование ограничений
        'uk': ''
    }
)

class Base(DeclarativeBase):
    metadata = metadata

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)   # Проверить допограничения (unique etc.)
    currency: Mapped[str] = mapped_column(String(4), nullable=False)

class Consumption(Base):
    __tablename__ = 'consumptions'

    # Здесь нужен ForeignKey на User.id (он мб будет здесь как PK)
    data: Mapped[date] = mapped_column()    # Проверить корректность date
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    subcategory: Mapped[str | Optional] = mapped_column(String(50, nullable=True))   # Проверить Optional
    spent: Mapped[int] = mapped_column(nullable=False)