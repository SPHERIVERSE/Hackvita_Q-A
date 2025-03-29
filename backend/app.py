from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import CORS
from backend.database import db
from backend import routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)  # Enable CORS

db.init_app(app)

with app.app_context():
    db.create_all()  # Create tables if they don't exist

app.register_blueprint(routes.main_bp)  # Register routes

if __name__ == '__main__':
    app.run(debug=True)
