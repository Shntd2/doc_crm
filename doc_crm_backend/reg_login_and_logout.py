from werkzeug.utils import safe_join
import firebase_admin
from config import SECRET_KEY, PATH_TO_REG_LOGIN_PAGE, FIREBASE_API
from firebase_admin import credentials, firestore
from flask import Flask, Blueprint, request, jsonify, g, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import jwt
import datetime
import re
import os


app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])  # allows only requests from Reacts localhost:3000
bcrypt = Bcrypt(app)

# Firebase
cred = credentials.Certificate(FIREBASE_API)
firebase_admin.initialize_app(cred)

# Firestore database instance
db = firestore.client()

registration_app = Blueprint(
    'registration', __name__, static_folder='../doc_crm/doc_crm_frontend/build', static_url_path='/static'
)
# set the static folders path where static assets for React app are stored


# connects to the registration page in React part
@app.route('/', defaults={'path': PATH_TO_REG_LOGIN_PAGE})
@app.route('/<path:path>')
def serve(path):
    try:
        safe_path = os.path.normpath(path)  # normalizes the incoming path to prevent directory traversal attacks
        # checks if the incoming path is the same as the path to the registration page
        if safe_path == os.path.normpath(PATH_TO_REG_LOGIN_PAGE):
            # if it does, the function serves the file located at PATH_TO_REG_LOGIN_PAGE using send_from_directory
            return send_from_directory(os.path.dirname(PATH_TO_REG_LOGIN_PAGE),  # gives the directory of the file
                                       os.path.basename(PATH_TO_REG_LOGIN_PAGE))  # gives the name of the file
        if safe_path != '' and os.path.isfile(os.path.join(app.static_folder, safe_path)):
            # will deliver registration.js file located within the app.static_folder directory
            # by safely joining the requested safe_path to the app.static_folder
            return send_from_directory(app.static_folder, safe_join(app.static_folder, safe_path))
        else:
            # send index.html if file in PATH_TO_REG_LOGIN_PAGE is not found
            return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return f'Error serving {path}: {str(e)}', 500


# check if token is blacklisted
@app.before_request
def check_blacklist():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(' ')[1]
            decoded_token = jwt.decode(token, [SECRET_KEY], algorithms=['HS256'])

            # Check if the token is blacklisted
            blacklisted_token_ref = db.collection('blacklist').document(token)
            blacklisted_token_doc = blacklisted_token_ref.get()
            if blacklisted_token_doc.exists:
                return jsonify({'message': 'Token has been invalidated'}), 401

            g.current_user = decoded_token
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401


# registration endpoint
# takes JSON data from registration.js and creates a new user in Firestore
@registration_app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        name = data.get('name')
        surname = data.get('surname')
        email = data.get('email')
        password = data.get('password')
        company_name = data.get('companyName')

        # Basic validation
        if not name or not surname or not email or not password:
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if the email is valid
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return jsonify({'message': 'Invalid email address'}), 400

        # Check if the user already exists
        user_ref = db.collection('users').document(email)
        user_doc = user_ref.get()
        if user_doc.exists:
            return jsonify({'message': 'Email already registered'}), 400

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user_data = {
            'name': name,
            'surname': surname,
            'email': email,
            'password': hashed_password,
            'company_name': company_name
        }
        user_ref.set(user_data)

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


# Login endpoint
@registration_app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        # Basic validation
        if not email or not password:
            return jsonify({'message': 'Missing required fields'}), 400

        # get user from Firestore
        user_ref = db.collection('users').document(email)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({'message': 'Invalid email or password'}), 401

        user_data = user_doc.to_dict()

        # Check password
        if not bcrypt.check_password_hash(user_data['password'], password):
            return jsonify({'message': 'Invalid email or password'}), 401

        # Generate JWT token
        token = jwt.encode({
            'email': email,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)  # Token expires in 1 hour
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({'message': 'Login successful', 'token': token}), 200

    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


# Logout
@registration_app.route('/api/logout', methods=['POST'])
def logout():
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]

            # Add the token to the blacklist
            blacklist_ref = db.collection('blacklist').document(token)
            blacklist_ref.set({
                'token': token,
                'blacklisted_on': datetime.datetime.now(datetime.timezone.utc)
            })

            return jsonify({'message': 'Logout successful'}), 200
        else:
            return jsonify({'message': 'Token missing'}), 400

    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
