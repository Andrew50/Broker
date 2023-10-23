from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    data = {"message": "Hello from Python backend!"}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)