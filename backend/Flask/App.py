from flask import Flask, jsonify, request
from test import sample_fetch
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the CORS module
import sys
import os

# Add the path to the directory containing the 'Match' script
match_script_path = r'C:\dev\Broker\backend\scripts'
sys.path.append(match_script_path)

# Import the 'Match' script
from Match import Match
from flask import Flask

app = Flask(__name__)
CORS(app)






@app.route('/api/data', methods=['GET'])
def get_data():
    
    
    string = request.args.get('inputString')
    print(string)
    try:
        message = Match.compute(string)
    except FloatingPointError:
        message = ''
    print('done')
        
    return jsonify(data=message)
# @app.route('/api/data', methods=['POST'])
# def post_data():
#     # Handle POST request, you can access data using request.json
#     posted_data = request.json
#     return jsonify(posted_data)

if __name__ == '__main__':
    
    app.run()