import pymysql

class PyMySQLExtension:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # Configure pymysql based on your app's configuration
        self.db = pymysql.connect(
            host = app.config['MYSQL_HOST'],
            user = app.config['MYSQL_USER'],
            password = app.config['MYSQL_PASSWORD'],
            database = app.config['MYSQL_DB'],
            port = app.config['MYSQL_PORT'],
            cursorclass = pymysql.cursors.DictCursor
        )