from flask import Flask
from os import getenv

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = getenv("SECRET_KEY")

import routes