#!/user/bin/python

from flask import Flask, request, jsonify
from modelvmfinal import db
from modelvmfinal import createDataBase
from modelvmfinal import Details
import redis

import simplejson as json

#import sys;
#sys.path.append('/usr/local/lib/python2.7/dist-packages/MySQLdb/__init__.pyc')

app = Flask(__name__)

@app.route('/v1/expenses/<expense_id>',methods = ['GET', 'PUT', 'DELETE'])
def show_details(expense_id):

        details = Details.query.filter_by(id=expense_id).first_or_404()

        if request.method == 'GET':
            return jsonify({'id' : details.id,
                           'name' : details.name,
                           'email' : details.email,
                           'category' : details.category,
                           'description' : details.email,
                           'link': details.link,
                           'estimated_costs' : details.estimated_costs,
                           'submit_date' : details.submit_date,
                           'status' : details.status,
                           'decision_date':details.decision_date
                           })
        elif request.method == 'PUT':
            x = request.get_json(force=True)
            details.estimated_costs=x['estimated_costs']
            db.session.commit()
            return jsonify({'Status': True}), 202
        else:
            db.session.delete(details)
            db.session.commit()
            return jsonify({}), 204


@app.route('/v1/expenses', methods=['POST'])
def add_details():
	createDataBase()
	db.create_all()
        x = request.get_json(force=True)

        details = Details(name=x['name'],
                           email=x['email'],
                           category=x['category'],
                           description=x['description'],
                           link=x['link'],
                           estimated_costs=x['estimated_costs'],
                           submit_date=x['submit_date'],
                           status="pending",
                           decision_date="09-08-2016")


        db.session.add(details)
        db.session.commit()
        temp = {
            'id' : details.id,
            'name' : details.name,
            'email' : details.email,
            'category' : details.category,
            'description' : details.email,
            'link': details.link,
            'estimated_costs' : details.estimated_costs,
            'submit_date' : details.submit_date,
            'status' : details.status,
            'decision_date':details.decision_date
                           }
        return jsonify(temp), 201





if __name__ == '__main__':
    r = redis.Redis(host = '127.0.0.1',port = 6379,db = 0)
   # print ("Hello World2")
    r.set('1','5001')
    #print ("Hello World3")
    a = r.get('1')
    print a
    app.run(host = "0.0.0.0",debug = True,port = 5001)
    #print ("Hello World4")

