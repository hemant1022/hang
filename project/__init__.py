from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        # Add some sample products if the DB is empty
        from .models import Product
        if not Product.query.first():
            sample_products = [
                Product(name='Laptop', price=1200.00, description='A powerful and portable laptop for all your needs.'),
                Product(name='Smartphone', price=800.00, description='The latest smartphone with amazing features.'),
                Product(name='Headphones', price=150.00, description='Noise-cancelling over-ear headphones.'),
                Product(name='Smartwatch', price=250.00, description='Track your fitness and stay connected.'),
                Product(name='E-Reader', price=130.00, description='Read your favorite books on a glare-free display.'),
                Product(name='Bluetooth Speaker', price=70.00, description='Portable speaker with rich sound.')
            ]
            db.session.bulk_save_objects(sample_products)
            db.session.commit()

    return app
