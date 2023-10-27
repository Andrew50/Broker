from flask_cors import CORS
from flask import Flask, jsonify, request, make_response
from celery import Celery
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['broker_url']     = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['broker_url'])
celery.conf.update(app.config)
