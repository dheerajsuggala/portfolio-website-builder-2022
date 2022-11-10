from flask import Flask
# from flask_wtf.csrf import CSRFProtect
from flask_pymongo import PyMongo
import string
import secrets
import os

app = Flask(__name__)
# csrf = CSRFProtect(app)

app.secret_key = ''.join(secrets.choice(string.ascii_uppercase + string.digits)for i in range(28))

app.config['MONGO_URI'] = os.environ["DATABASE_URI"]

mongo = PyMongo(app)
users_accounts_col = mongo.db.portfolioaccounts
portfolio_details_col = mongo.db.portfoliodetails






