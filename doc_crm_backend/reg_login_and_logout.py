from werkzeug.utils import safe_join
import requests
from config import SECRET_KEY, PATH_TO_REG_LOGIN_PAGE, FIREBASE_API_URL, FIREBASE_CONFIG 
# import firebase
from flask import Flask, Blueprint, request, jsonify, g, send_from_directory
from flask_bcrypt import Bcrypt
import jwt
import datetime
import re
import os


app = Flask(__name__)
bcrypt = Bcrypt(app)

registration_app = Blueprint(
    'registration', __name__, static_folder='../doc_crm/doc_crm_frontend/build', static_url_path='/static'
)
# set the static folders path where static assets for React app are stored

# Helper function to interact with Firebase Realtime Database
def firebase_request(method, endpoint, data=None, params=None):
    try:
        url = f'{FIREBASE_API_URL}/{endpoint}.json'
        if method == 'GET':
            response = requests.get(url, params=params)
        elif method == 'PUT':
            response = requests.put(url, json=data, params=params)
        elif method == 'POST':
            response = requests.post(url, json=data, params=params)
        elif method == 'DELETE':
            response = requests.delete(url, params=params)
        else:
            raise ValueError('Unsupported HTTP method')
        
        response.raise_for_status()  # Raises a HTTPError if the response code is 4xx, 5xx
        return response.json() if response.text else None
    except requests.exceptions.RequestException as e:
        print(f"Firebase request error: {e}")
        return None


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
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            # check if token is blacklisted
            blacklist_response = firebase_request('GET', f'blacklist/{token}')
            if blacklist_response is not None:
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
        print(request.get_json())
        
        name = data.get('name')
        surname = data.get('surname')
        email = data.get('email')
        password = data.get('password')
        company_name = data.get('companyName')

        # Basic validation
        if not all([name, surname, email, password]):
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if the email is valid
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return jsonify({'message': 'Invalid email address'}), 400

        # Check if the user already exists
        user_response = firebase_request('GET', f'users/{email}', params={'key': FIREBASE_CONFIG['apiKey']})
        if user_response is not None:
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
        user_response = firebase_request('PUT', f'users/{email}', data=user_data, params={'key': FIREBASE_CONFIG['apiKey']})

        if user_response is not None:
            return jsonify({'message': 'User registered successfully'}), 201
        else:
            return jsonify({'message': 'Failed to register user'}), 500

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
        user_response = requests.get(f'{FIREBASE_API_URL}/users/{email}.json', params={'key': FIREBASE_CONFIG['apiKey']})
        if not user_response.ok or user_response.json() is None:
            return jsonify({'message': 'Invalid email or password'}), 401

        user_response = firebase_request('GET', f'users/{email}', params={'key': FIREBASE_CONFIG['apiKey']})
        if user_response is None or not bcrypt.check_password_hash(user_response['password'], password):
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
            blacklist_data = {
                'token': token,
                'blacklisted_on': datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            blacklist_response = firebase_request('PUT', f'blacklist/{token}', data=blacklist_data, params={'key': FIREBASE_CONFIG['apiKey']})

            if blacklist_response is not None:
                return jsonify({'message': 'Logout successful'}), 200
            else:
                return jsonify({'message': 'Failed to blacklist token'}), 500
        else:
            return jsonify({'message': 'Token missing'}), 400

    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
