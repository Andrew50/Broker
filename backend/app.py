
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from tasks.Data import Data
from tasks.Match import Match
from . import celery, app




@celery.task
def my_background_task(arg1, arg2):
    # some long running task here
    return 'working'

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
def get_data():
    ticker = request.args.get('ticker')
    dt = request.args.get('dt')
    tf = request.args.get('tf')
    message = Match.compute(ticker,dt,tf)
    return jsonify(data=message)

if __name__ == '__main__':
    app.run(debug = True)