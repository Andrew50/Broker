
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from tasks.Data import Data
from tasks.Match import Match
from tasks.test_task import background_task
import redis
from flask import Flask

from multiprocessing import Pool


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

#def return_match(val):
    
    


@app.route('/api/test2')
def start_task():
    #return jsonify(message=f"Task started, job id: {job.id}")
    return 'god'



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
    pool
    pool.apply_async(return_match)
    data = Match.compute(ticker,dt,tf)
    return jsonify(data=data)

if __name__ == '__main__':
    app.run(debug = True)



# @app.route('/api/match', methods=['GET'])
# def get_match():
#     ticker = request.args.get('ticker')
#     dt = request.args.get('dt')
#     tf = request.args.get('tf')
#     message = Match.compute(ticker,dt,tf)
#     return jsonify(data=message)

# if __name__ == '__main__':
#     app.run(debug = True)