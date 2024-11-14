# app.py
import os
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Delete existing database and migrations
if os.path.exists('subscriptions.db'):
    os.remove('subscriptions.db')
if os.path.exists('migrations'):
    import shutil
    shutil.rmtree('migrations')

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Store plain password
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)

# app.py - Update Subscription model
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    subscription_type = db.Column(db.String(20), nullable=False, default='monthly')  # 'monthly' or 'yearly'
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
@login_manager.user_loader
def load_user(user_id):
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
    
    previous_subscriptions = Subscription.query.filter_by(
        user_id=current_user.id, 
        is_active=False
    ).all()
    
    monthly_total = sum(s.amount for s in active_subscriptions if s.subscription_type == 'monthly')
    yearly_total = sum(s.amount for s in active_subscriptions if s.subscription_type == 'yearly')
    total_annual = monthly_total * 12 + yearly_total
    
    return render_template('index.html',
                         active_subscriptions=active_subscriptions,
                         previous_subscriptions=previous_subscriptions,
                         monthly_total=monthly_total,
                         yearly_total=yearly_total,
                         total_annual=total_annual)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:  # Plain password comparison
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password']  # Store plain password
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
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
    if request.method == 'POST':
        subscription = Subscription(
            name=request.form['name'],
            amount=float(request.form['amount']),
            subscription_type=request.form['subscription_type'],  # Add this line
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
    subscription = Subscription.query.get_or_404(id)
    if subscription.user_id != current_user.id:
        return redirect(url_for('index'))
    if request.method == 'POST':
        subscription.name = request.form['name']
        subscription.amount = float(request.form['amount'])
        subscription.subscription_type = request.form['subscription_type']  # Add this line
        subscription.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        db.session.commit()
        flash('Subscription updated successfully!')
        return redirect(url_for('index'))
    return render_template('edit_subscription.html', subscription=subscription)

@app.route('/delete_subscription/<int:id>')
@login_required
def delete_subscription(id):
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
    monthly_total = sum(s.amount for s in subscriptions 
                       if s.subscription_type == 'monthly' and s.is_active)
    yearly_total = sum(s.amount for s in subscriptions 
                      if s.subscription_type == 'yearly' and s.is_active)

    return render_template('debug.html',
                         users=users,
                         subscriptions=subscriptions,
                         monthly_total=monthly_total,
                         yearly_total=yearly_total)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)    # app.py
    from flask import Flask, render_template, request, redirect, url_for, flash
    from flask_sqlalchemy import SQLAlchemy
    from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
    from datetime import datetime
    from werkzeug.security import generate_password_hash, check_password_hash
    
    app = Flask(__name__, static_url_path='/static')
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
    db = SQLAlchemy(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Models
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password = db.Column(db.String(120), nullable=False)  # Store plain password
        subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    
    class Subscription(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(80), nullable=False)
        amount = db.Column(db.Float, nullable=False)
        end_date = db.Column(db.DateTime, nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Routes
    @app.route('/')
    @login_required
    def index():
        subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', subscriptions=subscriptions)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = User.query.filter_by(username=request.form['username']).first()
            if user and user.password == request.form['password']:  # Plain password comparison
                login_user(user)
                return redirect(url_for('index'))
            flash('Invalid username or password')
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            user = User(
                username=request.form['username'],
                password=request.form['password']  # Store plain password
            )
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!')
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
        if request.method == 'POST':
            subscription = Subscription(
                name=request.form['name'],
                amount=float(request.form['amount']),
                end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d'),
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
        subscription = Subscription.query.get_or_404(id)
        if subscription.user_id != current_user.id:
            return redirect(url_for('index'))
        if request.method == 'POST':
            subscription.name = request.form['name']
            subscription.amount = float(request.form['amount'])
            subscription.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
            db.session.commit()
            flash('Subscription updated successfully!')
            return redirect(url_for('index'))
        return render_template('edit_subscription.html', subscription=subscription)
    
    @app.route('/delete_subscription/<int:id>')
    @login_required
    def delete_subscription(id):
        subscription = Subscription.query.get_or_404(id)
        if subscription.user_id == current_user.id:
            db.session.delete(subscription)
            db.session.commit()
            flash('Subscription deleted successfully!')
        return redirect(url_for('index'))
    
    @app.route('/debug')
    def debug_db():
        users = User.query.all()
        subscriptions = Subscription.query.all()
        return render_template('debug.html', users=users, subscriptions=subscriptions)
    
    if __name__ == '__main__':
        with app.app_context():
            db.create_all()
        app.run(debug=True)