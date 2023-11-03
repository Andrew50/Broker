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

    def start_task(self, script_name):

##--------LINK SCRIPTS------------
        if script_name == 'get':
            func = Chart.get
        if script_name =='match':
            func = test_func.god

        data = request.json
        task_id = str(uuid.uuid4())
        def callback(result):
            print(result.get())
            self.tasks[task_id] = {'status': 'done', 'result': result.get()}
        task = self.pool.apply_async(func, args=data.get('args', []), kwds=data.get('kwargs', {}), callback=callback)
        self.tasks[task_id] = {'status': 'pending', 'result': task}
        return jsonify({'task_id': task_id})

    def get_status(self, task_id):
        task_info = self.tasks.get(task_id)
        if task_info is None:
            return jsonify({'status': 'not found'}), 404

       # elif task_info['status'] == 'done':# and task_info['result'].ready():
          #  #result = task_info['result'].get()
           # result = task_info['result']
           # task_info.update({'status': 'done', 'result': result})
        #3else:
        print(task_info)
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
