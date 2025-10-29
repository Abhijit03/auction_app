from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db
from models.user import User
from models.product import Product, Bid
from models.category import Category

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def restrict_to_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))

@admin_bp.route('/dashboard')
def dashboard():
    total_users = User.query.count()
    total_products = Product.query.count()
    active_products = Product.query.filter(Product.end_time > datetime.utcnow()).count()
    total_bids = Bid.query.count()
    
    # Recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         active_products=active_products,
                         total_bids=total_bids,
                         recent_users=recent_users,
                         recent_products=recent_products)

@admin_bp.route('/products')
def products():
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=all_products, categories=categories)

@admin_bp.route('/categories')
def categories():
    all_categories = Category.query.all()
    return render_template('admin/categories.html', categories=all_categories)

@admin_bp.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    
    if Category.query.filter_by(name=name).first():
        flash('Category already exists', 'error')
        return redirect(url_for('admin.categories'))
    
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    
    flash('Category added successfully', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/delete_category/<int:category_id>')
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Check if category has products
    if category.products.count() > 0:
        flash('Cannot delete category with existing products', 'error')
        return redirect(url_for('admin.categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/toggle_product/<int:product_id>')
def toggle_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = not product.is_active
    db.session.commit()
    
    status = "activated" if product.is_active else "deactivated"
    flash(f'Product {status} successfully', 'success')
    return redirect(url_for('admin.products'))