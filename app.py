import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from PIL import Image
import secrets

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register blueprints
from routes.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'error'

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    products = db.relationship('Product', backref='seller', lazy='dynamic')
    bids = db.relationship('Bid', backref='bidder', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    products = db.relationship('Product', backref='category', lazy='dynamic')

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    starting_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)
    
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    bids = db.relationship('Bid', backref='product', lazy='dynamic', order_by='Bid.amount.desc()')
    
    @property
    def time_remaining(self):
        now = datetime.utcnow()
        if self.end_time > now:
            return self.end_time - now
        return None
    
    @property
    def is_auction_active(self):
        return self.is_active and self.end_time > datetime.utcnow()

class Bid(db.Model):
    __tablename__ = 'bids'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

# Login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processors
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.context_processor
def inject_categories():
    categories = Category.query.all()
    return dict(categories=categories)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_image(file):
    if file and allowed_file(file.filename):
        # Generate random filename
        random_hex = secrets.token_hex(8)
        _, ext = os.path.splitext(file.filename)
        filename = random_hex + ext
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Resize and save image
        try:
            img = Image.open(file)
            img.thumbnail((800, 600))
            img.save(filepath)
            return f"uploads/{filename}"
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    return None

# Routes
# Database Information Routes
@app.route('/admin/database-info')
@login_required
def database_info():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get database statistics
    total_categories = Category.query.count()
    total_products = Product.query.count()
    total_users = User.query.count()
    total_bids = Bid.query.count()
    
    # Get category statistics
    category_stats = []
    categories = Category.query.all()
    for category in categories:
        product_count = Product.query.filter_by(category_id=category.id).count()
        category_stats.append({
            'name': category.name,
            'product_count': product_count
        })
    
    # Get top categories
    top_categories = []
    for category in categories:
        product_count = Product.query.filter_by(category_id=category.id).count()
        if product_count > 0:
            top_categories.append({
                'name': category.name,
                'description': category.description or 'No description',
                'product_count': product_count
            })
    
    # Sort by product count (descending)
    top_categories.sort(key=lambda x: x['product_count'], reverse=True)
    top_categories = top_categories[:5]  # Top 5 categories
    
    return render_template('admin/database_info.html',
                         total_categories=total_categories,
                         total_products=total_products,
                         total_users=total_users,
                         total_bids=total_bids,
                         category_stats=category_stats,
                         top_categories=top_categories)

# Special Categories Management
@app.route('/admin/special-categories')
@login_required
def special_categories():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # This would come from a SpecialCategory model in a real implementation
    # For now, we'll use static data
    special_categories_data = [
        {
            'id': 1,
            'name': 'Food & Homemade Products',
            'why_it_matters': 'Home-based sellers get a digital platform',
            'product_count': 15,
            'status': 'Active',
            'is_featured': False
        },
        {
            'id': 2,
            'name': 'Tools & Machinery',
            'why_it_matters': 'OLX doesn\'t allow; Indiamart is too B2B-heavy',
            'product_count': 28,
            'status': 'Active',
            'is_featured': False
        },
        {
            'id': 3,
            'name': 'Events & Rentals',
            'why_it_matters': 'Huge demand for wedding/party rental items',
            'product_count': 42,
            'status': 'Growing',
            'is_featured': False
        },
        {
            'id': 4,
            'name': 'Industrial & Wholesale',
            'why_it_matters': 'Merges retail & bulk; ideal for small manufacturers',
            'product_count': 67,
            'status': 'Partner',
            'is_featured': False
        },
        {
            'id': 5,
            'name': 'Travel & Tourism',
            'why_it_matters': 'Book local cabs, rooms, and packages in one place',
            'product_count': 23,
            'status': 'Active',
            'is_featured': False
        },
        {
            'id': 6,
            'name': 'Education & Coaching',
            'why_it_matters': 'A hub for tutors, coaching, classes & materials',
            'product_count': 34,
            'status': 'Educational',
            'is_featured': False
        },
        {
            'id': 7,
            'name': 'Plants & Gardening',
            'why_it_matters': 'Gardening is trending - no OLX category exists for this',
            'product_count': 19,
            'status': 'Active',
            'is_featured': False
        },
        {
            'id': 8,
            'name': 'Art, Collectibles & Antiques',
            'why_it_matters': 'Vintage, rare items need a home - OLX blocks most',
            'product_count': 56,
            'status': 'Active',
            'is_featured': False
        },
        {
            'id': 9,
            'name': 'DIY & Handmade',
            'why_it_matters': 'Promote local craft & culture - Indian Etsy alternative',
            'product_count': 89,
            'status': 'Featured',
            'is_featured': True
        }
    ]
    
    return render_template('admin/special_categories.html', 
                         special_categories=special_categories_data)

@app.route('/admin/add-special-category', methods=['GET', 'POST'])
@login_required
def add_special_category():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Handle special category creation
        name = request.form.get('name')
        why_it_matters = request.form.get('why_it_matters')
        status = request.form.get('status')
        is_featured = bool(request.form.get('is_featured'))
        
        # In a real implementation, you would save to SpecialCategory model
        flash(f'Special category "{name}" added successfully!', 'success')
        return redirect(url_for('special_categories'))
    
    return render_template('admin/add_special_category.html')

# Add these routes for completeness
@app.route('/admin/edit-special-category/<int:category_id>')
@login_required
def edit_special_category(category_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    flash('Edit functionality would be implemented here', 'info')
    return redirect(url_for('special_categories'))

@app.route('/admin/delete-special-category/<int:category_id>')
@login_required
def delete_special_category(category_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    flash('Delete functionality would be implemented here', 'info')
    return redirect(url_for('special_categories'))

@app.route('/')
def home():
    active_products = Product.query.filter(
        Product.end_time > datetime.utcnow(),
        Product.is_active == True
    ).order_by(Product.created_at.desc()).limit(8).all()
    
    categories = Category.query.all()
    return render_template('home.html', products=active_products, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        
        flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        # First user becomes admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('home'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).all()
    user_bids = Bid.query.filter_by(user_id=current_user.id).order_by(Bid.created_at.desc()).all()
    
    return render_template('dashboard.html', products=user_products, bids=user_bids)

@app.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        starting_price = float(request.form.get('starting_price'))
        category_id = int(request.form.get('category_id'))
        end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        
        image_url = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                image_url = save_image(image_file)
        
        product = Product(
            name=name,
            description=description,
            starting_price=starting_price,
            current_price=starting_price,
            image_url=image_url,
            end_time=end_time,
            seller_id=current_user.id,
            category_id=category_id
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product listed for auction successfully!', 'success')
        return redirect(url_for('home'))
    
    categories = Category.query.all()
    min_date = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
    max_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M')
    
    return render_template('add_product.html', categories=categories, min_date=min_date, max_date=max_date)

@app.route('/product/<int:product_id>')
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('view_prod.html', product=product)

@app.route('/product/bid/<int:product_id>', methods=['POST'])
@login_required
def place_bid(product_id):
    product = Product.query.get_or_404(product_id)
    
    if not product.is_auction_active:
        return jsonify({'success': False, 'error': 'Auction has ended'})
    
    if current_user.id == product.seller_id:
        return jsonify({'success': False, 'error': 'You cannot bid on your own product'})
    
    try:
        bid_amount = float(request.form.get('bid_amount'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Invalid bid amount'})
    
    if bid_amount <= product.current_price:
        return jsonify({'success': False, 'error': f'Bid must be higher than current price (${product.current_price})'})
    
    # Create new bid
    bid = Bid(amount=bid_amount, user_id=current_user.id, product_id=product.id)
    product.current_price = bid_amount
    
    db.session.add(bid)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Bid placed successfully!',
        'new_price': product.current_price,
        'bid_count': product.bids.count()
    })

@app.route('/category/<int:category_id>')
def products_by_category(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).order_by(Product.created_at.desc()).all()
    return render_template('category_products.html', category=category, products=products)

# Admin routes are now handled by the admin blueprint

# Initialize database
with app.app_context():
    db.create_all()
    
    # Create default admin user if not exists
    admin_user = User.query.filter_by(email='admin@auction.com').first()
    if not admin_user:
        admin_user = User(username='admin', email='admin@auction.com', is_admin=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Create default categories
        categories = [
            Category(name='Electronics', description='Electronic devices and accessories'),
            Category(name='Fashion', description='Clothing and fashion items'),
            Category(name='Home & Garden', description='Home and garden products'),
            Category(name='Sports', description='Sports equipment and gear'),
            Category(name='Collectibles', description='Rare and collectible items'),
        ]
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        print("Default admin user created: admin@auction.com / admin123")
  
if __name__ == '__main__':
    # Export models for create_sample_data.py
    __all__ = ['app', 'db', 'User', 'Product', 'Category', 'Bid']
    
    port = int(os.environ.get('PORT', 8000))
    print("🚀 Starting Auction Application...")
    print("📊 Initializing SQLite Database...")
    app.run(host='0.0.0.0', port=port)