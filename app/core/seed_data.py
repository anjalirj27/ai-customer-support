from datetime import datetime, timedelta
from sqlalchemy import select

from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment
from app.schemas.common import OrderStatus, PaymentStatus


async def seed_demo_data(db):
    # Check if users already exist
    result = await db.execute(select(User))
    if result.scalars().first():
        return  # Data already present

    # Create user
    user = User(email="demo@example.com", name="Demo User")
    db.add(user)
    await db.flush()

    # Create order
    order = Order(
        user_id=user.id,
        order_number="ORD-2024-002",
        status=OrderStatus.SHIPPED,
        items=[{"name": "Phone", "quantity": 1, "price": 25000}],
        total_amount=25000,
        shipping_address={"city": "Delhi"},
        tracking_number="TRK987654321",
        estimated_delivery=datetime.utcnow() + timedelta(days=2)
    )
    db.add(order)

    # Create payment
    payment = Payment(
        user_id=user.id,
        invoice_number="INV-2024-002",
        amount=25000,
        status=PaymentStatus.COMPLETED,
        payment_method="upi",
        description="Payment for ORD-2024-002"
    )
    db.add(payment)

    await db.commit()
