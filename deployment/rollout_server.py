from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/rollout', methods=['POST'])
def rollout():
    try:
        os.chdir('/home/aj/dev/Broker')
        result = subprocess.run(['bash', 'rollout'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"status": "success", "output": result.stdout}), 200
        else:
            return jsonify({"status": "error", "output": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
