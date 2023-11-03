from flask import Flask, jsonify, request
from flask_cors import CORS
from scripts import Data
from multiprocessing import Pool
import uuid
from scripts import Data, Chart, test_func

class App:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.pool = Pool()
        self.tasks = {}
        self.cores = 6
        
        


    def start_task(self, script_name):

##--------LINK SCRIPTS------------
        if script_name == 'get':
            func = Chart.get
            cores = 1
        elif script_name =='match':
            func = test_func.god
            cores = 3
        else:
            return jsonify({'task_id': 'failed'})
        data = request.json
        task_id = str(uuid.uuid4())
        def callback(result):
            self.tasks[task_id] = {'status': 'done', 'result': result}
        #for _ in range(cores):
        task = self.pool.apply(func, args=data.get('args', []), kwds=data.get('kwargs', {}))#, callback=callback)
        self.tasks[task_id] = {'status': 'pending', 'result': task}
        return jsonify({'task_id': task_id})

    def get_status(self, task_id):
        task_info = self.tasks.get(task_id)
        try: 
            return jsonify(task_info)
        except:
            return jsonify('loading')
            

    def run(self):
        @self.app.route('/api/<script_name>', methods=['POST'])
        def route_start_task(script_name):
            return self.start_task(script_name)

        @self.app.route('/api/status/<task_id>', methods=['GET'])
        def route_get_status(task_id):
            return self.get_status(task_id)

        self.app.run(debug=True, port=5000)

if __name__ == '__main__':
    app = App()
    app.run()
