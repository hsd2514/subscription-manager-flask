# cli_init.py
from app import app, db, User, Subscription
from datetime import datetime

def init_db_cli():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Users with simple passwords
        users = [
            User(username='rahul', password='pass'),
            User(username='priya', password='pass'),
            User(username='amit', password='pass'),
            User(username='neha', password='pass')
        ]
        db.session.add_all(users)
        db.session.commit()

        # Subscriptions with active and inactive status
        subscriptions = [
            # Rahul's subscriptions
            Subscription(
                name='Netflix Premium',
                amount=649,
                subscription_type='monthly',
                end_date=datetime(2024, 12, 31),
                is_active=True,
                user_id=1
            ),
            Subscription(
                name='Amazon Prime',
                amount=1499,
                subscription_type='yearly',
                end_date=datetime(2024, 12, 31),
                is_active=True,
                user_id=1
            ),
            Subscription(
                name='Hotstar',
                amount=1499,
                subscription_type='yearly',
                end_date=datetime(2023, 12, 31),
                is_active=False,
                user_id=1
            ),

            # Priya's subscriptions
            Subscription(
                name='Hotstar',
                amount=299,
                subscription_type='monthly',
                end_date=datetime(2024, 6, 30),
                is_active=True,
                user_id=2
            ),
            Subscription(
                name='Spotify Family',
                amount=179,
                subscription_type='monthly',
                end_date=datetime(2024, 12, 31),
                is_active=True,
                user_id=2
            ),
            Subscription(
                name='Netflix Basic',
                amount=199,
                subscription_type='monthly',
                end_date=datetime(2023, 11, 30),
                is_active=False,
                user_id=2
            ),

            # Amit's subscriptions
            Subscription(
                name='Spotify',
                amount=119,
                subscription_type='monthly',
                end_date=datetime(2024, 12, 31),
                is_active=True,
                user_id=3
            ),
            Subscription(
                name='YouTube Premium',
                amount=129,
                subscription_type='monthly',
                end_date=datetime(2024, 8, 31),
                is_active=True,
                user_id=3
            ),
            Subscription(
                name='Amazon Prime',
                amount=1499,
                subscription_type='yearly',
                end_date=datetime(2023, 10, 31),
                is_active=False,
                user_id=3
            ),

            # Neha's subscriptions
            Subscription(
                name='Netflix Premium',
                amount=649,
                subscription_type='monthly',
                end_date=datetime(2024, 7, 31),
                is_active=True,
                user_id=4
            ),
            Subscription(
                name='Swiggy One',
                amount=899,
                subscription_type='yearly',
                end_date=datetime(2024, 12, 31),
                is_active=True,
                user_id=4
            ),
            Subscription(
                name='Spotify',
                amount=119,
                subscription_type='monthly',
                end_date=datetime(2023, 9, 30),
                is_active=False,
                user_id=4
            )
        ]
        db.session.add_all(subscriptions)
        db.session.commit()
        print("Database initialized with dummy data!")

if __name__ == '__main__':
    init_db_cli()