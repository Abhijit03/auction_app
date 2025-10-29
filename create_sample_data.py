import os
import sys
from datetime import datetime, timedelta
from random import choice, randint

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from the main app file
from app import app, db, User, Product, Category

def create_sample_data():
    with app.app_context():
        print("🔄 Creating sample data for unique categories...")
        
        # First, create or update categories to match your structure
        categories_data = [
            {
                "name": "Food & Homemade Products",
                "description": "Home-based sellers get a digital platform"
            },
            {
                "name": "Tools & Machinery", 
                "description": "OLX doesn't allow; Indiamart is too B2B-heavy"
            },
            {
                "name": "Events & Rentals",
                "description": "Huge demand for wedding/party rental items"
            },
            {
                "name": "Industrial & Wholesale",
                "description": "Merges retail & bulk; ideal for small manufacturers - MET Bhujbal Knowledge City"
            },
            {
                "name": "Travel & Tourism",
                "description": "Book local cabs, rooms, and packages in one place"
            },
            {
                "name": "Education & Coaching", 
                "description": "A hub for tutors, coaching, classes & materials - MET'S INSTITUTE OF MANAGEMENT"
            },
            {
                "name": "Plants & Gardening",
                "description": "Gardening is trending - no OLX category exists for this"
            },
            {
                "name": "Art, Collectibles & Antiques",
                "description": "Vintage, rare items need a home - OLX blocks most"
            },
            {
                "name": "DIY & Handmade",
                "description": "Indian Etsy - promote local craft & culture"
            }
        ]
        
        # Update or create categories
        print("📝 Setting up unique categories...")
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data["name"]).first()
            if category:
                category.description = cat_data["description"]
                print(f"✅ Updated category: {cat_data['name']}")
            else:
                category = Category(name=cat_data["name"], description=cat_data["description"])
                db.session.add(category)
                print(f"✅ Created category: {cat_data['name']}")
        
        db.session.commit()
        
        # Get all categories
        categories = {cat.name: cat for cat in Category.query.all()}
        print(f"📊 Total categories: {len(categories)}")
        
        # Get users (create sample users if none exist)
        users = User.query.all()
        if len(users) < 5:
            print("👥 Creating sample users...")
            sample_users = [
                {"username": "home_chef_priya", "email": "priya@example.com", "password": "password123"},
                {"username": "tools_expert_raj", "email": "raj@example.com", "password": "password123"},
                {"username": "event_planner_sneha", "email": "sneha@example.com", "password": "password123"},
                {"username": "met_student_amit", "email": "amit@example.com", "password": "password123"},
                {"username": "artisan_rohit", "email": "rohit@example.com", "password": "password123"}
            ]
            
            for user_data in sample_users:
                if not User.query.filter_by(email=user_data["email"]).first():
                    user = User(
                        username=user_data["username"],
                        email=user_data["email"]
                    )
                    user.set_password(user_data["password"])
                    db.session.add(user)
                    print(f"✅ Created user: {user_data['username']}")
            
            db.session.commit()
            users = User.query.all()
            print(f"📊 Total users: {len(users)}")

        # Sample products tailored to your unique categories
        sample_products = [
            # Food & Homemade Products
            {
                "name": "Homemade Gujarati Dhokla Kit",
                "description": "Authentic Gujarati dhokla preparation kit with fresh ingredients and traditional recipe. Perfect for breakfast or snacks.",
                "starting_price": 299,
                "category": "Food & Homemade Products",
                "image": "dhokla_kit.jpg"
            },
            {
                "name": "Artisanal Chocolate Truffles (12 pieces)",
                "description": "Handcrafted Belgian chocolate truffles with Indian flavors like cardamom and saffron. Made with love in home kitchen.",
                "starting_price": 450,
                "category": "Food & Homemade Products", 
                "image": "chocolate_truffles.jpg"
            },
            {
                "name": "Traditional Maharashtrian Pickles Set",
                "description": "3 varieties of homemade pickles - Mango, Lemon, and Mixed Vegetable. No preservatives, traditional recipe.",
                "starting_price": 350,
                "category": "Food & Homemade Products",
                "image": "pickles_set.jpg"
            },

            # Tools & Machinery
            {
                "name": "Professional Power Drill Kit",
                "description": "Heavy-duty power drill perfect for home DIY projects. Includes drill bits and carrying case.",
                "starting_price": 2500,
                "category": "Tools & Machinery",
                "image": "power_drill.jpg"
            },
            {
                "name": "CNC Wood Cutting Machine",
                "description": "Small CNC machine for woodworking and craft projects. Perfect for small workshops and hobbyists.",
                "starting_price": 15000,
                "category": "Tools & Machinery",
                "image": "cnc_machine.jpg"
            },
            {
                "name": "Industrial Sewing Machine",
                "description": "Heavy-duty sewing machine for leather and denim. Ideal for small tailoring businesses.",
                "starting_price": 8000,
                "category": "Tools & Machinery", 
                "image": "sewing_machine.jpg"
            },

            # Events & Rentals
            {
                "name": "Wedding Decoration Package",
                "description": "Complete wedding decoration package including mandap, lighting, and floral arrangements. For 200 guests.",
                "starting_price": 25000,
                "category": "Events & Rentals",
                "image": "wedding_decor.jpg"
            },
            {
                "name": "Sound System Rental - Party Events",
                "description": "Professional sound system with speakers, mixer, and microphones. Perfect for parties and corporate events.",
                "starting_price": 5000,
                "category": "Events & Rentals",
                "image": "sound_system.jpg"
            },
            {
                "name": "Photography Studio Rental (4 hours)",
                "description": "Fully equipped photography studio with lighting, backdrops, and basic props. Perfect for portfolio shoots.",
                "starting_price": 2000,
                "category": "Events & Rentals",
                "image": "studio_rental.jpg"
            },

            # Industrial & Wholesale
            {
                "name": "MET Engineering Project Kits (Wholesale)",
                "description": "Bulk purchase of engineering project kits for MET students. Minimum order 10 units.",
                "starting_price": 15000,
                "category": "Industrial & Wholesale", 
                "image": "project_kits.jpg"
            },
            {
                "name": "Textile Fabric Lot - Wholesale",
                "description": "Mixed fabric lot from Surat textile market. Perfect for small clothing manufacturers.",
                "starting_price": 20000,
                "category": "Industrial & Wholesale",
                "image": "fabric_lot.jpg"
            },

            # Travel & Tourism
            {
                "name": "Lonavala Weekend Package",
                "description": "2-day package including stay, meals, and local sightseeing. Perfect weekend getaway from Mumbai.",
                "starting_price": 3999,
                "category": "Travel & Tourism",
                "image": "lonavala_package.jpg"
            },
            {
                "name": "Local Mumbai Tour Guide Service",
                "description": "Experienced guide for Mumbai city tours. Customizable itineraries available.",
                "starting_price": 1500,
                "category": "Travel & Tourism",
                "image": "tour_guide.jpg"
            },

            # Education & Coaching
            {
                "name": "MET Management Entrance Coaching",
                "description": "Complete coaching package for MET entrance exam. Includes study material and mock tests.",
                "starting_price": 15000,
                "category": "Education & Coaching",
                "image": "met_coaching.jpg"
            },
            {
                "name": "Programming Bootcamp - Python & Django",
                "description": "Intensive 6-week programming course. Perfect for MET computer science students.",
                "starting_price": 8000,
                "category": "Education & Coaching",
                "image": "programming_bootcamp.jpg"
            },

            # Plants & Gardening
            {
                "name": "Indoor Plants Starter Kit",
                "description": "Set of 5 air-purifying indoor plants with pots and care guide. Perfect for apartments.",
                "starting_price": 1200,
                "category": "Plants & Gardening",
                "image": "indoor_plants.jpg"
            },
            {
                "name": "Organic Terrace Gardening Setup",
                "description": "Complete setup for organic vegetable gardening on terrace. Includes containers, soil, and seeds.",
                "starting_price": 3500,
                "category": "Plants & Gardening", 
                "image": "terrace_garden.jpg"
            },

            # Art, Collectibles & Antiques
            {
                "name": "Vintage Bollywood Poster Collection",
                "description": "Rare collection of original Bollywood movie posters from 1970s-80s. Excellent condition.",
                "starting_price": 15000,
                "category": "Art, Collectibles & Antiques",
                "image": "bollywood_posters.jpg"
            },
            {
                "name": "Antique Brass Idols Set",
                "description": "Beautiful antique brass idols from Rajasthan. Authentic vintage pieces.",
                "starting_price": 8000,
                "category": "Art, Collectibles & Antiques",
                "image": "brass_idols.jpg"
            },

            # DIY & Handmade (Featured Category)
            {
                "name": "Handmade Leather Journal",
                "description": "Beautiful handcrafted leather journal with traditional Indian motifs. Perfect for writers.",
                "starting_price": 1200,
                "category": "DIY & Handmade",
                "image": "leather_journal.jpg"
            },
            {
                "name": "Macrame Wall Hanging - Handmade",
                "description": "Intricate macrame wall hanging made with natural cotton rope. Bohemian home decor.",
                "starting_price": 1800,
                "category": "DIY & Handmade",
                "image": "macrame_wall.jpg"
            },
            {
                "name": "Hand-painted Silk Saree",
                "description": "Exclusive hand-painted silk saree with traditional Kalamkari art. One of a kind piece.",
                "starting_price": 4500,
                "category": "DIY & Handmade",
                "image": "painted_saree.jpg"
            }
        ]

        print("📦 Creating category-specific products...")
        products_created = 0
        
        for product_data in sample_products:
            # Check if product already exists
            if not Product.query.filter_by(name=product_data["name"]).first():
                category = categories.get(product_data["category"])
                if not category:
                    print(f"❌ Category '{product_data['category']}' not found")
                    continue
                
                # Create product
                product = Product(
                    name=product_data["name"],
                    description=product_data["description"],
                    starting_price=product_data["starting_price"],
                    current_price=product_data["starting_price"],
                    image_url=f"uploads/{product_data['image']}",
                    end_time=datetime.utcnow() + timedelta(days=randint(3, 30)),
                    seller_id=choice(users).id,
                    category_id=category.id,
                    is_active=True
                )
                
                db.session.add(product)
                products_created += 1
                print(f"✅ Created product: {product_data['name']}")
        
        db.session.commit()
        print(f"🎉 Created {products_created} category-specific products")
        
        # Print summary
        print("\n" + "="*50)
        print("📊 DATABASE SUMMARY")
        print("="*50)
        for cat_name, category in categories.items():
            count = Product.query.filter_by(category_id=category.id).count()
            print(f"📁 {cat_name}: {count} products")
        print("="*50)
        print(f"👥 Total Users: {User.query.count()}")
        print(f"📦 Total Products: {Product.query.count()}")
        print("🎉 Sample data creation completed!")

if __name__ == "__main__":
    create_sample_data()