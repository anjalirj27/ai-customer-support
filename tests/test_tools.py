import uuid
from datetime import datetime

from sqlalchemy import select

from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.schemas.common import OrderStatus, PaymentStatus
from app.tools.billing_tools import CheckRefundStatusTool, ProcessRefundTool
from app.tools.order_tools import CancelOrderTool, FetchOrderDetailsTool, ModifyOrderTool


async def make_user(db) -> User:
    user = User(email=f"{uuid.uuid4().hex}@example.com", name="Test User")
    db.add(user)
    await db.commit()
    return user


async def make_order(db, status=OrderStatus.PENDING, number="ORD-1") -> Order:
    user = await make_user(db)
    order = Order(
        user_id=user.id,
        order_number=number,
        status=status,
        items=[{"name": "Phone", "quantity": 1, "price": 100}],
        total_amount=100,
        shipping_address={"city": "Delhi", "zip": "110001"},
        estimated_delivery=datetime(2030, 1, 1),
    )
    db.add(order)
    await db.commit()
    return order


async def make_payment(db, status=PaymentStatus.COMPLETED, amount=100.0, refunded=0.0) -> Payment:
    user = await make_user(db)
    payment = Payment(
        user_id=user.id,
        invoice_number="INV-1",
        amount=amount,
        status=status,
        payment_method="upi",
        refund_amount=refunded,
    )
    db.add(payment)
    await db.commit()
    return payment


async def test_fetch_order_includes_estimated_delivery(db):
    await make_order(db)
    result = await FetchOrderDetailsTool(db).execute("ORD-1")
    assert result.success
    assert result.data["estimated_delivery"].startswith("2030-01-01")


async def test_cancel_pending_order_persists(db):
    await make_order(db, OrderStatus.PENDING)
    result = await CancelOrderTool(db).execute("ORD-1", reason="changed mind")

    assert result.success
    stored = (await db.execute(select(Order))).scalar_one()
    assert stored.status == OrderStatus.CANCELLED


async def test_cancel_shipped_order_is_rejected(db):
    await make_order(db, OrderStatus.SHIPPED)
    result = await CancelOrderTool(db).execute("ORD-1")

    assert not result.success
    assert "shipped" in result.error
    stored = (await db.execute(select(Order))).scalar_one()
    assert stored.status == OrderStatus.SHIPPED


async def test_cancel_already_cancelled_order(db):
    await make_order(db, OrderStatus.CANCELLED)
    result = await CancelOrderTool(db).execute("ORD-1")
    assert not result.success
    assert "already cancelled" in result.error


async def test_cancel_unknown_order(db):
    result = await CancelOrderTool(db).execute("NOPE")
    assert not result.success


async def test_modify_shipping_address_merges_fields(db):
    await make_order(db, OrderStatus.CONFIRMED)
    result = await ModifyOrderTool(db).execute("ORD-1", {"shipping_address": {"city": "Mumbai"}})

    assert result.success
    stored = (await db.execute(select(Order))).scalar_one()
    assert stored.shipping_address == {"city": "Mumbai", "zip": "110001"}


async def test_modify_rejects_shipped_order_and_unsupported_fields(db):
    await make_order(db, OrderStatus.SHIPPED)
    assert not (await ModifyOrderTool(db).execute("ORD-1", {"shipping_address": {"city": "X"}})).success

    await db.execute(Order.__table__.update().values(status=OrderStatus.PENDING))
    await db.commit()
    assert not (await ModifyOrderTool(db).execute("ORD-1", {"items": []})).success


async def test_full_refund(db):
    await make_payment(db, amount=100.0)
    result = await ProcessRefundTool(db).execute("INV-1", reason="defective")

    assert result.success
    stored = (await db.execute(select(Payment))).scalar_one()
    assert stored.status == PaymentStatus.REFUNDED
    assert stored.refund_amount == 100.0


async def test_partial_refund_then_remainder(db):
    await make_payment(db, amount=100.0)
    tool = ProcessRefundTool(db)

    assert (await tool.execute("INV-1", reason="partial", amount=40.0)).success
    stored = (await db.execute(select(Payment))).scalar_one()
    assert stored.status == PaymentStatus.PARTIALLY_REFUNDED

    too_much = await tool.execute("INV-1", reason="again", amount=70.0)
    assert not too_much.success

    assert (await tool.execute("INV-1", reason="rest")).success
    await db.refresh(stored)
    assert stored.status == PaymentStatus.REFUNDED
    assert stored.refund_amount == 100.0


async def test_refund_rejected_for_pending_payment_and_bad_amounts(db):
    await make_payment(db, status=PaymentStatus.PENDING)
    tool = ProcessRefundTool(db)
    assert not (await tool.execute("INV-1", reason="x")).success

    await db.execute(Payment.__table__.update().values(status=PaymentStatus.COMPLETED))
    await db.commit()
    assert not (await tool.execute("INV-1", reason="x", amount=0)).success
    assert not (await tool.execute("INV-1", reason="x", amount=-5)).success


async def test_check_refund_status_reflects_database(db):
    await make_payment(db, status=PaymentStatus.COMPLETED)
    tool = CheckRefundStatusTool(db)
    assert (await tool.execute("INV-1")).data["is_refunded"] is False

    await ProcessRefundTool(db).execute("INV-1", reason="x")
    result = await tool.execute("INV-1")
    assert result.data["is_refunded"] is True
    assert result.data["refund_amount"] == 100.0
