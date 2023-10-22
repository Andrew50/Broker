from flask import Flask, send_from_directory
import random
numbers= [1,2,3,4,5,6];
app = Flask(__name__)

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)

@app.route("/rand")
def hello():
    return str(numbers)

if __name__ == "__main__":
    app.run(debug=True)