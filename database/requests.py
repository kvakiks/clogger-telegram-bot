from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Consumption, User


async def get_or_create_user(session: AsyncSession, tg_user_id: int, currency: str) -> User:
    user = await session.scalar(select(User).where(User.tg_id == tg_user_id))
    if not user:
        user = User(tg_id=tg_user_id, currency=currency)
        session.add(user)
    await session.commit()
    return user


async def add_expense(session: AsyncSession, tg_user_id: int, category: str, amount: int) -> int:
    user = await session.scalar(select(User).where(User.tg_id == tg_user_id))
    if not user:
        return False

    expense = Consumption(consumer_id=user.tg_id, category=category, spent=amount)
    session.add(expense)
    await session.commit()
    return True

# Возмонжо эта функция не нужна больше
async def get_total_spent_for_days(session: AsyncSession, tg_user_id: int, days: int) -> int:
    start_date = date.today() - timedelta(days=days - 1)
    total = await session.scalar(
        select(func.coalesce(func.sum(Consumption.spent), 0)).where(
            Consumption.consumer_id == tg_user_id,
            Consumption.created_at >= start_date,
        )
    )
    return int(total or 0)


async def get_spending_by_category_for_days(
    session: AsyncSession, tg_user_id: int, days: int
) -> tuple[list[tuple[str, int]], int]:
    start_date = date.today() - timedelta(days=days - 1)
    stmt = (
        select(Consumption.category, func.sum(Consumption.spent))
        .where(
            Consumption.consumer_id == tg_user_id,
            Consumption.created_at >= start_date,
        )
        .group_by(Consumption.category)
        .order_by(func.sum(Consumption.spent).desc())
    )
    rows = await session.execute(stmt)
    breakdown = [(cat, int(s or 0)) for cat, s in rows.all()]
    total = sum(amount for _, amount in breakdown)
    return breakdown, total


async def get_users_count(session: AsyncSession) -> int:
    count = await session.scalar(select(func.count(User.tg_id)))
    return int(count or 0)


async def get_users_list(session: AsyncSession, limit: int = 100) -> list[User]:
    result = await session.scalars(select(User).order_by(User.tg_id).limit(limit))
    return list(result)