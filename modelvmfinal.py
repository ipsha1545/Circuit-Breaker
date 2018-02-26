from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
import MySQLdb

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123@localhost/Details'
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

class Details(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(500))
        email = db.Column(db.String(600))
        category = db.Column(db.String(900))
        description = db.Column(db.String(700))
        link = db.Column(db.String(700))
        estimated_costs = db.Column(db.String(150))
        submit_date = db.Column(db.String(100))
        status = db.Column(db.String(200))
        decision_date = db.Column(db.String(300))





def createDataBase():
    import sqlalchemy
    try:
        engine = sqlalchemy.create_engine('mysql://root:123@localhost') # connect to server
        engine.execute("CREATE DATABASE IF NOT EXISTS Details") #create db
    except:
        print "error in above line"


if __name__ == '__main__':
	app.run()
