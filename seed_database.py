import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.common import (
    OrderStatus, 
    PaymentStatus, 
    ConversationStatus,
    MessageRole,
    AgentType
)

async def seed_data():
    """Sample data seed karega"""
    
    print("Seeding database with mock data...\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if data already exists
            result = await db.execute(select(User))
            existing_users = result.scalars().all()
            
            if existing_users:
                print("Database already has data!")
                print(f"Found {len(existing_users)} existing users.")
                response = input("Do you want to add more data? (yes/no): ")
                if response.lower() != 'yes':
                    print("Seeding cancelled.")
                    return
            
            # Create Users
            print("👥 Creating users...")
            users = [
                User(
                    email="anjali.sharma@example.com",
                    name="Anjali Sharma"
                ),
                User(
                    email="rahul.verma@example.com",
                    name="Rahul Verma"
                ),
                User(
                    email="priya.singh@example.com",
                    name="Priya Singh"
                )
            ]
            
            for user in users:
                db.add(user)
            
            await db.flush()  # Get IDs without committing
            print(f"Created {len(users)} users")
            
            # Create Orders
            print("\nCreating orders...")
            orders = [
                # User 1 orders
                Order(
                    user_id=users[0].id,
                    order_number="ORD-2024-001",
                    status=OrderStatus.DELIVERED,
                    items=[
                        {"name": "Laptop", "quantity": 1, "price": 55000},
                        {"name": "Mouse", "quantity": 1, "price": 500}
                    ],
                    total_amount=55500,
                    shipping_address={
                        "street": "123 MG Road",
                        "city": "Bangalore",
                        "state": "Karnataka",
                        "pincode": "560001"
                    },
                    tracking_number="TRK123456789",
                    estimated_delivery=datetime.utcnow() - timedelta(days=5),
                    created_at=datetime.utcnow() - timedelta(days=10)
                ),
                Order(
                    user_id=users[0].id,
                    order_number="ORD-2024-002",
                    status=OrderStatus.SHIPPED,
                    items=[
                        {"name": "Phone", "quantity": 1, "price": 25000}
                    ],
                    total_amount=25000,
                    shipping_address={
                        "street": "123 MG Road",
                        "city": "Bangalore",
                        "state": "Karnataka",
                        "pincode": "560001"
                    },
                    tracking_number="TRK987654321",
                    estimated_delivery=datetime.utcnow() + timedelta(days=2),
                    created_at=datetime.utcnow() - timedelta(days=2)
                ),
                
                # User 2 orders
                Order(
                    user_id=users[1].id,
                    order_number="ORD-2024-003",
                    status=OrderStatus.PENDING,
                    items=[
                        {"name": "Headphones", "quantity": 2, "price": 2000}
                    ],
                    total_amount=4000,
                    shipping_address={
                        "street": "456 Park Street",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400001"
                    },
                    tracking_number=None,
                    estimated_delivery=None,
                    created_at=datetime.utcnow()
                ),
                Order(
                    user_id=users[1].id,
                    order_number="ORD-2024-004",
                    status=OrderStatus.CANCELLED,
                    items=[
                        {"name": "Tablet", "quantity": 1, "price": 15000}
                    ],
                    total_amount=15000,
                    shipping_address={
                        "street": "456 Park Street",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400001"
                    },
                    tracking_number=None,
                    estimated_delivery=None,
                    created_at=datetime.utcnow() - timedelta(days=3)
                ),
                
                # User 3 orders
                Order(
                    user_id=users[2].id,
                    order_number="ORD-2024-005",
                    status=OrderStatus.CONFIRMED,
                    items=[
                        {"name": "Smartwatch", "quantity": 1, "price": 12000},
                        {"name": "Earbuds", "quantity": 1, "price": 3000}
                    ],
                    total_amount=15000,
                    shipping_address={
                        "street": "789 Ring Road",
                        "city": "Delhi",
                        "state": "Delhi",
                        "pincode": "110001"
                    },
                    tracking_number=None,
                    estimated_delivery=datetime.utcnow() + timedelta(days=5),
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
            ]
            
            for order in orders:
                db.add(order)
            
            await db.flush()
            print(f"Created {len(orders)} orders")
            
            # Create Payments
            print("\n💳 Creating payments...")
            payments = [
                Payment(
                    user_id=users[0].id,
                    invoice_number="INV-2024-001",
                    amount=55500,
                    status=PaymentStatus.COMPLETED,
                    payment_method="credit_card",
                    description="Payment for Order ORD-2024-001",
                    created_at=datetime.utcnow() - timedelta(days=10)
                ),
                Payment(
                    user_id=users[0].id,
                    invoice_number="INV-2024-002",
                    amount=25000,
                    status=PaymentStatus.COMPLETED,
                    payment_method="upi",
                    description="Payment for Order ORD-2024-002",
                    created_at=datetime.utcnow() - timedelta(days=2)
                ),
                Payment(
                    user_id=users[1].id,
                    invoice_number="INV-2024-003",
                    amount=4000,
                    status=PaymentStatus.PENDING,
                    payment_method="credit_card",
                    description="Payment for Order ORD-2024-003",
                    created_at=datetime.utcnow()
                ),
                Payment(
                    user_id=users[1].id,
                    invoice_number="INV-2024-004",
                    amount=15000,
                    status=PaymentStatus.REFUNDED,
                    payment_method="debit_card",
                    description="Payment for Order ORD-2024-004 (Cancelled)",
                    refund_amount=15000,
                    refund_reason="Order cancelled by customer",
                    created_at=datetime.utcnow() - timedelta(days=3)
                ),
                Payment(
                    user_id=users[2].id,
                    invoice_number="INV-2024-005",
                    amount=15000,
                    status=PaymentStatus.COMPLETED,
                    payment_method="netbanking",
                    description="Payment for Order ORD-2024-005",
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
            ]
            
            for payment in payments:
                db.add(payment)
            
            await db.flush()
            print(f"Created {len(payments)} payments")
            
            # Create Sample Conversation
            print("\nCreating sample conversation...")
            
            conversation = Conversation(
                user_id=users[0].id,
                title="Order Tracking Query",
                status=ConversationStatus.RESOLVED,
                extra_data={
                    "total_messages": 4,
                    "agents_used": ["router", "order"]
                }
            )
            db.add(conversation)
            await db.flush()
            
            # Add messages to conversation
            messages = [
                Message(
                    conversation_id=conversation.id,
                    role=MessageRole.USER,
                    content="Hi, I want to check my order status",
                    created_at=datetime.utcnow() - timedelta(minutes=10)
                ),
                Message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content="Hello! I'd be happy to help you check your order status. Could you please provide your order number?",
                    agent_type=AgentType.ROUTER,
                    created_at=datetime.utcnow() - timedelta(minutes=9)
                ),
                Message(
                    conversation_id=conversation.id,
                    role=MessageRole.USER,
                    content="It's ORD-2024-002",
                    created_at=datetime.utcnow() - timedelta(minutes=8)
                ),
                Message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content="Great! I found your order ORD-2024-002. Your order for Phone (₹25,000) has been shipped! Your tracking number is TRK987654321 and the estimated delivery date is in 2 days.",
                    agent_type=AgentType.ORDER,
                    tool_calls=[
                        {
                            "tool": "fetch_order_details",
                            "params": {"order_number": "ORD-2024-002"}
                        }
                    ],
                    extra_data={
                        "confidence": 0.95,
                        "reasoning": "User provided order number, fetched from database"
                    },
                    created_at=datetime.utcnow() - timedelta(minutes=7)
                )
            ]
            
            for message in messages:
                db.add(message)
            
            print(f" Created 1 conversation with {len(messages)} messages")
            
            # Commit all changes
            await db.commit()
            
            print("\n" + "="*50)
            print("🎉 Database seeded successfully!")
            print("="*50)
            print(f"\nSummary:")
            print(f"   • Users: {len(users)}")
            print(f"   • Orders: {len(orders)}")
            print(f"   • Payments: {len(payments)}")
            print(f"   • Conversations: 1")
            print(f"   • Messages: {len(messages)}")
            
            print("\n Sample Data:")
            print("\n   Users:")
            for user in users:
                print(f"      - {user.name} ({user.email})")
            
            print("\n   Orders:")
            for order in orders:
                print(f"      - {order.order_number}: {order.status.value.upper()} - ₹{order.total_amount}")
            
            print("\n   Payments:")
            for payment in payments:
                print(f"      - {payment.invoice_number}: {payment.status.value.upper()} - ₹{payment.amount}")
            
        except Exception as e:
            await db.rollback()
            print(f"\nError seeding database: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(seed_data())