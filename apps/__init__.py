from flask import Flask
from flask_login import LoginManager
from ext.pymysql_ext import PyMySQLExtension
from flask_pymongo import PyMongo
from importlib import import_module
from . import config

mysql = PyMySQLExtension()
login_manager = LoginManager()
mongo = PyMongo()

def register_extensions(app):
    mysql.init_app(app)
    login_manager.init_app(app)
    mongo.init_app(app)

def register_blueprints(app): 
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

def configure_database(app):
    try:
        # MySQL
        app.config['MYSQL_HOST']        = config.DB_HOST
        app.config['MYSQL_USER']        = config.DB_USERNAME
        app.config['MYSQL_PASSWORD']    = config.DB_PASS
        app.config['MYSQL_DB']          = config.DB_NAME
        app.config['MYSQL_PORT']        = config.DB_PORT

        # Mongo DB
        app.config["MONGO_URI"]         = "mongodb://localhost:27017/databaseProject"

    except Exception as e:
        print('> Error: Database not loaded - Exception: ' + str(e) )

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    configure_database(app)
    register_extensions(app)
    register_blueprints(app)
    return app
