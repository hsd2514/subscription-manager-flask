# app.py
import os
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

def init_app():
    # Initialize Flask app
    app = Flask(__name__)
    
    # Ensure instance folder exists
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Configure app
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "subscriptions.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'harsh.dange23@vit.edu'  # Update this
    app.config['MAIL_PASSWORD'] = 'aimg vkkv xnhv jmxo'     # Update this
    
    return app

# Create app
app = init_app()

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Models
class User(UserMixin, db.Model):
    """User model for storing user credentials and linking subscriptions"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Add email field
    password = db.Column(db.String(120), nullable=False)  # Storing plain password
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)

class Subscription(db.Model):
    """Subscription model for tracking user subscriptions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Amount in INR
    subscription_type = db.Column(db.String(20), nullable=False)  # 'monthly' or 'yearly'
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback"""
    return User.query.get(int(user_id))

# Initialize migration
migrate = Migrate(app, db)

# Routes
@app.route('/')
@login_required
def index():
    active_subscriptions = Subscription.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).all()
    
    inactive_subscriptions = Subscription.query.filter_by(
        user_id=current_user.id, 
        is_active=False
    ).all()
    
    monthly_total = sum(s.amount for s in active_subscriptions if s.subscription_type == 'monthly')
    yearly_total = sum(s.amount for s in active_subscriptions if s.subscription_type == 'yearly')
    total_annual = monthly_total * 12 + yearly_total
    
    return render_template('index.html',
                         active_subscriptions=active_subscriptions,
                         inactive_subscriptions=inactive_subscriptions,
                         monthly_total=monthly_total,
                         yearly_total=yearly_total,
                         total_annual=total_annual)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        # Simple password check
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']     # Keep email for registration
        password = request.form['password']
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        # Create new user with email
        user = User(
            username=username,
            email=email,           # Include email
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_subscription', methods=['GET', 'POST'])
@login_required
def add_subscription():
    """Add new subscription for current user"""
    if request.method == 'POST':
        # Create new subscription from form data
        subscription = Subscription(
            name=request.form['name'],
            amount=float(request.form['amount']),
            subscription_type=request.form['subscription_type'],
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d'),
            is_active=True,
            user_id=current_user.id
        )
        db.session.add(subscription)
        db.session.commit()
        flash('Subscription added successfully!')
        return redirect(url_for('index'))
    return render_template('add_subscription.html')

@app.route('/edit_subscription/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subscription(id):
    """Edit existing subscription"""
    subscription = Subscription.query.get_or_404(id)
    # Verify subscription belongs to current user
    if subscription.user_id != current_user.id:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        # Update subscription details
        subscription.name = request.form['name']
        subscription.amount = float(request.form['amount'])
        subscription.subscription_type = request.form['subscription_type']
        subscription.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        db.session.commit()
        flash('Subscription updated successfully!')
        return redirect(url_for('index'))
    return render_template('edit_subscription.html', subscription=subscription)

@app.route('/delete_subscription/<int:id>')
@login_required
def delete_subscription(id):
    """Delete subscription if it belongs to current user"""
    subscription = Subscription.query.get_or_404(id)
    if subscription.user_id == current_user.id:
        db.session.delete(subscription)
        db.session.commit()
        flash('Subscription deleted successfully!')
    return redirect(url_for('index'))

# app.py - Update debug route
@app.route('/debug')
def debug():
    users = User.query.all()
    subscriptions = Subscription.query.all()
    
    # Calculate totals
    monthly_total = sum(s.amount for s in subscriptions if s.subscription_type == 'monthly' and s.is_active)
    yearly_total = sum(s.amount for s in subscriptions if s.subscription_type == 'yearly' and s.is_active)
    
    return render_template('debug.html',
                         users=users,
                         subscriptions=subscriptions,
                         monthly_total=monthly_total,
                         yearly_total=yearly_total)

# app.py - Update send_test_email route
@app.route('/send_test_email')
def send_test_email():
    try:
        rahul = User.query.filter_by(username='rahul').first()
        if not rahul:
            return 'User Rahul not found'
            
        active_subs = Subscription.query.filter_by(user_id=rahul.id, is_active=True).all()
        
        msg = Message(
            'Your Active Subscriptions',
            sender=app.config['MAIL_USERNAME'],
            recipients=['harshdange25@gmail.com']
        )
        
        # HTML Email template with inline styles
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    Subscription Update
                </h2>
                
                <p style="font-size: 16px; margin: 20px 0;">
                    Dear <strong>{rahul.username}</strong>,
                </p>
                
                <p style="margin-bottom: 20px;">
                    Here are your active subscriptions:
                </p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
        """
        
        for sub in active_subs:
            html_content += f"""
                <div style="background: white; padding: 15px; margin-bottom: 15px; border-left: 4px solid #3498db; border-radius: 3px;">
                    <h3 style="color: #2c3e50; margin: 0 0 10px 0;">{sub.name}</h3>
                    <p style="margin: 5px 0;">
                        <span style="color: #7f8c8d;">Amount:</span> 
                        <strong style="color: #27ae60;">₹{sub.amount:.2f}</strong>
                    </p>
                    <p style="margin: 5px 0;">
                        <span style="color: #7f8c8d;">Type:</span> 
                        <span style="background: #e8f4f8; padding: 2px 8px; border-radius: 12px; font-size: 14px;">
                            {sub.subscription_type}
                        </span>
                    </p>
                    <p style="margin: 5px 0;">
                        <span style="color: #7f8c8d;">End Date:</span> 
                        <span style="color: #e74c3c;">{sub.end_date.strftime('%Y-%m-%d')}</span>
                    </p>
                </div>
            """
        
        html_content += """
                </div>
                
                <p style="margin-top: 20px; color: #7f8c8d; font-size: 14px;">
                    This is an automated message from your Subscription Manager.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.html = html_content
        mail.send(msg)
        return 'Styled test email sent successfully!'
        
    except Exception as e:
        return f'Error sending email: {str(e)}'

@app.route('/test_email')
def test_email():
    try:
        msg = Message(
            'Test Email',
            sender=app.config["MAIL_USERNAME"],
            recipients=['harshdange25@gmail.com']  # Replace with your test email
        )
        msg.body = 'This is a test email from Flask-Mail'
        mail.send(msg)
        return 'Mail sent!'
    except Exception as e:
        return str(e)

def check_expiring_subscriptions():
    """Check for subscriptions expiring tomorrow and send notifications"""
    with app.app_context():
        tomorrow = datetime.now().date() + timedelta(days=1)
        expiring_subs = Subscription.query.filter(
            Subscription.end_date.date() == tomorrow,
            Subscription.is_active == True
        ).all()

        for sub in expiring_subs:
            user = User.query.get(sub.user_id)
            msg = Message(
                'Subscription Expiring Tomorrow',
                sender=app.config['MAIL_USERNAME'],
                recipients=[user.email]  # Add email field to User model
            )
            msg.body = f"""
            Dear {user.username},
            
            Your subscription for {sub.name} is expiring tomorrow.
            Amount: ₹{sub.amount}
            Type: {sub.subscription_type}
            End Date: {sub.end_date.strftime('%Y-%m-%d')}
            
            Please renew if you wish to continue the service.
            
            Regards,
            Subscription Manager
            """
            mail.send(msg)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_expiring_subscriptions, trigger="interval", hours=24)
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error creating database: {e}")
    app.run(debug=True)