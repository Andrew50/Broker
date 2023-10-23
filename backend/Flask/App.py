from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    # Sample data to be returned for GET request
    message = {
        "message": "Hello, JSON!",
        "status": "success"
    }

    # Using jsonify to convert the dictionary to JSON and send it as the response
    return jsonify(message)

if __name__ == '__main__':
    app.run()