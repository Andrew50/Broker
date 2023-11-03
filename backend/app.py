from flask import Flask, jsonify, request
from flask_cors import CORS
from multiprocessing import Pool
import uuid
#import Chart, Data, Match, Screener, Settings, Study, Trainer
import importlib

class App:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.pool = Pool()
        self.tasks = {}
        self.cores = 6
        
        


    def start_task(self, script_name):

        module_name, function_name = script_name.split('-')
        module = importlib.import_module(module_name)
        func = getattr(module, function_name, None)
        args = request.args.to_dict()
        task_id = str(uuid.uuid4())
        def callback(result):
            self.tasks[task_id] = {'status': 'done', 'result': result}
        #for _ in range(cores):
        task = self.pool.apply_async(func, args=args, callback=callback)
        #task = self.pool.apply(func, args=args)
        self.tasks[task_id] = {'status': 'pending', 'result': task}
        return jsonify({'task_id': task_id})

    def get_status(self, task_id):
        task_info = self.tasks.get(task_id)
        try: 
            return jsonify(task_info)
        except Exception as e:
            print(e)
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
