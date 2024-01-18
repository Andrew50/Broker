from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/rollout', methods=['POST'])
def rollout():
    try:
        # Change to the desired directory
        os.chdir('/path/to/your/directory')

        # Run the script
        print("Running rollout script...")
        result = subprocess.run(['bash', 'rollout'], capture_output=True, text=True)

        # Return the result
        return jsonify({"status": "success", "output": result.stdout}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
