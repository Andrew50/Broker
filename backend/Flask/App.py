from flask import Flask, jsonify, request
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the CORS module
import sys
import os
import collections

# Add the path to the directory containing the 'Match' script
aj = True
if aj:
    match_script_path = r'C:\dev\Broker\backend\scripts'
else:
    match_script_path = r'C:\Users\owens\Documents\Broker2\backend\scripts'
# match_script_path = r'C:\dev\Broker\backend\scripts'
sys.path.append(match_script_path)

# Import the 'Match' script
from Match import Match
from flask import Flask
from Data import Data

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# message = [
#   {
#     "ID": 1,
#     "Name": "Alice",
#     "Department": "HR",
#     "Salary": 50000
#   },
#   {
#     "ID": 2,
#     "Name": "Bob",
#     "Department": "Sales",
#     "Salary": 60000
#   },
#   {
#     "ID": 3,
#     "Name": "Charlie",
#     "Department": "Engineering",
#     "Salary": 75000
#   }
# ]
@app.route('/api/get', methods=['GET'])
def get_ticker():
    ticker = request.args.get('ticker')
    tf = request.args.get('tf')
    #
    dt = None#request.args.get('dt')
    df = Data(ticker,tf,dt).df
    df = df.reset_index()
    
    df['time'] = df['datetime'].dt.date
    df['time'] = df['time'].astype(str)
    df = df[['time','open','high','low','close']]
    print(df)
    #df = df.to_dict(orient='records')
    #df = collections.OrderedDict(df.to_records(index=False))
    #message = jsonify(data=df)
    message =  df.to_json(orient='records')
    return message

@app.route('/api/match', methods=['GET'])
def get_data():
    ticker = request.args.get('ticker')
    dt = request.args.get('dt')
    tf = request.args.get('tf')
    message = Match.compute(ticker,dt,tf)
    #message = 'working'

    message = jsonify(data=message)
    print(f'message: {message}')
    return message
# @app.route('/api/data', methods=['POST'])
# def post_data():
#     # Handle POST request, you can access data using request.json
#     posted_data = request.json
#     return jsonify(posted_data)

if __name__ == '__main__':
    
    app.run()