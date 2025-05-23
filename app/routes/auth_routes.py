from flask import Blueprint, request, jsonify, current_app
from app.models.user import User
from app.utils.database import db
from app.services.auth import generate_token, authenticate, decode_token
from functools import wraps

auth_bp = Blueprint("auth", __name__)

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Missing or invalid token'}), 401
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    user = User(username=data['username'], role=data.get('role', 'student'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = authenticate(data['username'], data['password'])
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    token = generate_token(user)
    return jsonify({'token': token})

