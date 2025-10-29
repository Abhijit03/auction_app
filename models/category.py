from models import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    products = db.relationship('Product', backref='category_rel', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'