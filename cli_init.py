# dummy_data.py
from app import app, db, User, Subscription
from datetime import datetime, timedelta

def init_dummy_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create users with emails
        users = [
            User(username='rahul', password='pass', email='rahul@example.com'),
            User(username='priya', password='pass', email='priya@example.com'),
            User(username='amit', password='pass', email='amit@example.com'),
            User(username='neha', password='pass', email='neha@example.com')
        ]
        db.session.add_all(users)
        db.session.commit()

        # Create subscriptions
        subscriptions = [
            # Rahul's active subscriptions
            Subscription(
                name='Netflix Premium',
                amount=649,
                subscription_type='monthly',
                end_date=datetime.now() + timedelta(days=1),  # Expiring tomorrow
                is_active=True,
                user_id=1
            ),
            Subscription(
                name='Amazon Prime',
                amount=1499,
                subscription_type='yearly',
                end_date=datetime.now() + timedelta(days=30),
                is_active=True,
                user_id=1
            ),
            
            # Rahul's inactive subscription
            Subscription(
                name='Hotstar',
                amount=1499,
                subscription_type='yearly',
                end_date=datetime.now() - timedelta(days=30),
                is_active=False,
                user_id=1
            ),

            # Priya's subscriptions
            Subscription(
                name='Spotify Family',
                amount=179,
                subscription_type='monthly',
                end_date=datetime.now() + timedelta(days=15),
                is_active=True,
                user_id=2
            ),
            Subscription(
                name='YouTube Premium',
                amount=129,
                subscription_type='monthly',
                end_date=datetime.now() - timedelta(days=5),
                is_active=False,
                user_id=2
            ),

            # Amit's subscriptions
            Subscription(
                name='Zomato Pro',
                amount=900,
                subscription_type='yearly',
                end_date=datetime.now() + timedelta(days=1),  # Expiring tomorrow
                is_active=True,
                user_id=3
            ),

            # Neha's subscriptions
            Subscription(
                name='Netflix Basic',
                amount=199,
                subscription_type='monthly',
                end_date=datetime.now() + timedelta(days=20),
                is_active=True,
                user_id=4
            ),
            Subscription(
                name='Amazon Prime',
                amount=1499,
                subscription_type='yearly',
                end_date=datetime.now() - timedelta(days=10),
                is_active=False,
                user_id=4
            )
        ]
        db.session.add_all(subscriptions)
        db.session.commit()
        
        print("Dummy data initialized successfully!")

if __name__ == '__main__':
    init_dummy_data()