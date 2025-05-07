"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Test endpoint
@app.route('/user', methods=['GET'])
def handle_hello():
    return jsonify({"msg": "Hello, this is your GET /user response"}), 200

# ----------------- STARWARS API -----------------

# GET all characters
@app.route('/people', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    return jsonify([char.serialize() for char in characters]), 200

# GET character by ID
@app.route('/people/<int:people_id>', methods=['GET'])
def get_character_by_id(people_id):
    character = Character.query.get(people_id)
    if character:
        return jsonify(character.serialize()), 200
    return jsonify({"error": "Character not found"}),

# GET all planets
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

# GET planet by ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    return jsonify({"error": "Planet not found"}), 404

# GET all users
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# GET favorites of the first user (mock user)
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = User.query.first()  # ⚠️ Usuario actual (sin autenticación)
    if not user:
        return jsonify({"msg": "No users in the database"}), 404
    return jsonify([fav.serialize() for fav in user.favorites]), 200

# POST favorite planet
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user = User.query.first()  # ⚠️ Usuario actual fijo
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    fav = Favorite(user_id=user.id, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201

# POST favorite character
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):
    user = User.query.first()
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    fav = Favorite(user_id=user.id, character_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201

# DELETE favorite planet
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user = User.query.first()
    fav = Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first()
    if not fav:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite planet deleted"}), 200

# DELETE favorite character
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(people_id):
    user = User.query.first()
    fav = Favorite.query.filter_by(user_id=user.id, character_id=people_id).first()
    if not fav:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite character deleted"}), 200
