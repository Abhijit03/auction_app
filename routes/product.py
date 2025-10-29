from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from PIL import Image
from models import db
from models.product import Product, Bid
from models.category import Category
from config.config import Config

product_bp = Blueprint('product', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to make filename unique
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Resize image to max 800x600
        try:
            img = Image.open(file)
            img.thumbnail((800, 600))
            img.save(filepath)
            return f"uploads/{filename}"
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    return None

@product_bp.route('/add', methods=['GET', 'POST'])
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
    
    return render_template('add_product.html', 
                         categories=categories,
                         min_date=min_date,
                         max_date=max_date)

@product_bp.route('/product/<int:product_id>')
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('view_prod.html', product=product)

@product_bp.route('/bid/<int:product_id>', methods=['POST'])
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

@product_bp.route('/category/<int:category_id>')
def products_by_category(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).order_by(Product.created_at.desc()).all()
    return render_template('category_products.html', category=category, products=products)