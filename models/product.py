from datetime import datetime
from models import db

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
    
    # Foreign Keys
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relationships
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
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Bid(db.Model):
    __tablename__ = 'bids'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def __repr__(self):
        return f'<Bid ${self.amount} by User {self.user_id}>'