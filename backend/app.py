#app.py
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
# from tasks.Data import Data
# from tasks.Match import Match
from flask import Flask
from flask import Flask, jsonify, request
import redis
from rq import Queue
from multiprocessing import Pool
import time
from flask import Flask, jsonify, request
from huey import RedisHuey
from tasks import add_numbers
from database import Data


app = Flask(__name__)
CORS(app)
huey = RedisHuey('app')



@app.route('/api/add', methods=['POST'])
def add():
    data = request.json
    num1 = data.get('num1')
    num2 = data.get('num2')
    
    # Dispatch the task to Huey
    result = add_numbers((num1, num2), delay=5)
    return jsonify({"message": "Task is in queue, will be processed in 5 seconds.", "id": result.id})


@app.route('/api/get2', methods=['GET'])
def get_ticker():
    ticker = request.args.get('ticker')
    tf = request.args.get('tf')
    dt = None#request.args.get('dt')
    df = Data(ticker,tf,dt).df
    df = df.reset_index()
    df['time'] = df['datetime']
    df['time'] = df['time'].astype(str)
    df = df[['time','open','high','low','close']]
    message =  df.to_json(orient='records')
    return message





@app.route('/api/get', methods=['GET'])
def get_ticker():
    ticker = request.args.get('ticker')
    tf = request.args.get('tf')
    dt = None#request.args.get('dt')
    df = Data(ticker,tf,dt).df
    df = df.reset_index()
    df['time'] = df['datetime']
    df['time'] = df['time'].astype(str)
    df = df[['time','open','high','low','close']]
    message =  df.to_json(orient='records')
    return message


@app.route('/api/match', methods=['GET'])
def get_match():
    ticker = request.args.get('ticker')
    dt = request.args.get('dt')
    tf = request.args.get('tf')
    data = Match.compute(ticker,dt,tf)
    return jsonify(data=data)

if __name__ == '__main__':
    app.run(debug = True)

