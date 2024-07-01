import os
from dotenv import load_dotenv


load_dotenv()

# APPLICATION_URL = os.getenv('APPLICATION_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
# FIREBASE_ADMIN_SDK = os.getenv('FIREBASE_ADMIN_SDK')
PATH_TO_REG_LOGIN_PAGE = os.getenv('PATH_TO_REG_LOGIN_PAGE')
