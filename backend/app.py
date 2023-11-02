from flask import Flask, jsonify, request
from flask_cors import CORS
from multiprocessing import Pool
import uuid
from scripts import Data
#from scripts import Match  # Ensure the scripts module is in your Python path
from scripts import test_func
class App:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.pool = Pool()
        self.tasks = {}

    def start_task(self, script_name):
      

##--------DEFINE SCRIPTS------------
        if script_name == 'get':
            func = Data.Data
        if script_name =='match':
            func = test_func.god


        data = request.json
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        task_id = str(uuid.uuid4())
        def callback(result):
            self.tasks[task_id] = {'status': 'done', 'result': result}
        task = self.pool.apply_async(func, args=args, kwds=kwargs, callback=callback)
        self.tasks[task_id] = {'status': 'pending', 'task': task}
        return jsonify({'task_id': task_id})

    def get_status(self, task_id):
        task_info = self.tasks.get(task_id)
        if task_info is None:
            return jsonify({'status': 'not found'}), 404

        if task_info['status'] == 'pending' and task_info['task'].ready():
            result = task_info['task'].get()
            task_info.update({'status': 'done', 'result': result})

        return jsonify(task_info)

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
