
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from tasks.Data import Data
from tasks.Match import Match
from tasks.test_task import background_task
import redis
from flask import Flask
from flask import Flask, jsonify, request
import redis
from rq import Queue
from multiprocessing import Pool
import time
from flask import Flask, jsonify, request
from huey import RedisHuey

app = Flask(__name__)
CORS(app)
huey = RedisHuey('my_app', host='localhost')

@app.route('/api/enqueue', methods=['POST'])
def enqueue():
    data = request.json
    task = async_task(data['value'])
    return jsonify({"task_id": task.id}), 202

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    result = async_task.result(task_id)
    if result is None:
        return jsonify({"status": "pending"})
    if result:
        if result.error:
            return jsonify({"status": "error", "error": str(result.error)})
        return jsonify({"status": "finished", "result": result.data})
    return jsonify({"status": "not found"})

@huey.task()
def async_task(value):
    print("Processing:", value)
    time.sleep(5)
    print("Done processing:", value)
    return {"processed_value": value}

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

