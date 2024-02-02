from flask import Flask, request, jsonify
import subprocess
import os
import traceback
import datetime
from multiprocessing import Process, Queue

app = Flask(__name__)

@app.route('/rollout', methods=['POST'])
def rollout():
    try:
        print(f"{datetime.datetime.now()} Rollout request received", flush=True)
        os.chdir('/home/aj/dev/Broker/deployment/prod')

        # Create a queue to communicate the result
        result_queue = Queue()

        # Define a function to run the rollout script
        def run_rollout(queue):
            result = subprocess.run(['bash', 'rollout'], capture_output=True, text=True)
            queue.put(result)

        # Start the rollout script in a separate process
        rollout_process = Process(target=run_rollout, args=(result_queue,))
        rollout_process.start()

        # Return the request immediately
        return jsonify({"status": "queued"}), 202

    except Exception as e:
        print(str(e), flush=True)
        return jsonify({"status": "error", "message": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)