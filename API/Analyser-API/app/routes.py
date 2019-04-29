from app import app
from flask import jsonify


@app.route('/')
def index():
    return jsonify({'response': True, 'message': 'API is online'})
