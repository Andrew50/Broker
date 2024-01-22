from flask import Flask, request, jsonify
import subprocess
import os
import traceback

app = Flask(__name__)

@app.route('/rollout', methods=['POST'])
def rollout():
    try:
        print("Rollout request received", flush=True)
        os.chdir('/home/aj/dev/Broker/deployment/prod')
        result = subprocess.run(['bash', 'rollout'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"status": "success", "output": result.stdout}), 200
        else:
            raise Exception(result.stderr)
    except Exception as e:
        print(str(e), flush=True)
        return jsonify({"status": "error", "message": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)