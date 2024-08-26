from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from extensions import db, ma

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    ma.init_app(app)

    Migrate(app, db)

    from routes import vehicle_bookings_bp
    
    app.register_blueprint(vehicle_bookings_bp)

    return app
