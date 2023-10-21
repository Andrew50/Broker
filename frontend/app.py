from flask import Flask, send_from_directory
from views import views

app = Flask(__name__)
app.register_blueprint(views, url_prefix ="/")



@app.route("/")
def base():
    return send_from_directory('./', 'index.html')


if __name__ == "__main__":
    app.run(debug= True, port=8000)
