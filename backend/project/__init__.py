from flask import Flask

from .views import main
from .utils import make_celery

def create_app():
    app = Flask(__name__)
    
    #app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
   # app.config["SECRET_KEY"] = "Oz8Z7Iu&DwoQK)g%*Wit2YpE#-46vy0n"
    app.config["SECRET_KEY"] = "key"
    app.config["CELERY_CONFIG"] = {"broker_url": 'redis://localhost:6379/0', "result_backend": 'redis://localhost:6379/0'}

    #db.init_app(app)

    celery = make_celery(app)
    celery.set_default()
    
    app.register_blueprint(main)

    return app, celery