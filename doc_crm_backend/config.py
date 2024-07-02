import os
from dotenv import load_dotenv


load_dotenv()

# APPLICATION_URL = os.getenv('APPLICATION_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
FIREBASE_API_URL = os.getenv('FIREBASE_API_URL')
FIREBASE_CONFIG = os.getenv('FIREBASE_CONFIG')
PATH_TO_REG_LOGIN_PAGE = os.getenv('PATH_TO_REG_LOGIN_PAGE')
