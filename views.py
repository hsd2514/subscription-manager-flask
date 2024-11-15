import argparse
from tabulate import tabulate
from colorama import init, Fore
from app import User, Subscription, db, app  # Import app

init()  # Initialize colorama

def get_users():
    with app.app_context():  # Add context manager
        users = User.query.all()
        headers = ['ID', 'Username', 'Email']
        data = [[u.id, u.username, u.email] for u in users]
        return tabulate(data, headers=headers, tablefmt='grid')

def get_subscriptions(active_only=False):
    with app.app_context():  # Add context manager
        query = Subscription.query
        if active_only:
            query = query.filter_by(is_active=True)
        subs = query.all()
        
        headers = ['ID', 'User', 'Type', 'Amount', 'Status']
        data = []
        for s in subs:
            status = Fore.GREEN + 'Active' if s.is_active else Fore.RED + 'Inactive'
            data.append([s.id, s.user.username, s.subscription_type, 
                        f"₹{s.amount:.2f}", status + Fore.RESET])
        return tabulate(data, headers=headers, tablefmt='grid')

def get_totals():
    with app.app_context():  # Add context manager
        subs = Subscription.query.filter_by(is_active=True).all()
        monthly = sum(s.amount for s in subs if s.subscription_type == 'monthly')
        yearly = sum(s.amount for s in subs if s.subscription_type == 'yearly')
        
        data = [
            ['Monthly Total', f"₹{monthly:.2f}"],
            ['Yearly Total', f"₹{yearly:.2f}"],
            ['Total', f"₹{monthly + yearly:.2f}"]
        ]
        return tabulate(data, tablefmt='grid')

def main():
    parser = argparse.ArgumentParser(description='Subscription Management Views')
    parser.add_argument('view', choices=['users', 'subs', 'active-subs', 'totals'],
                       help='View to display (users/subs/active-subs/totals)')
    
    args = parser.parse_args()
    
    if args.view == 'users':
        print("\nUsers:")
        print(get_users())
    elif args.view == 'subs':
        print("\nAll Subscriptions:")
        print(get_subscriptions())
    elif args.view == 'active-subs':
        print("\nActive Subscriptions:")
        print(get_subscriptions(active_only=True))
    elif args.view == 'totals':
        print("\nSubscription Totals:")
        print(get_totals())

if __name__ == '__main__':
    main()