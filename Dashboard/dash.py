from flask import Blueprint, render_template, redirect, request
from flask_login import login_required, logout_user
from allParts import AllParts
from __init__ import db, cache
from sqlalchemy.orm import sessionmaker
import json
import time
import datetime

Dash_bp = Blueprint('Dash__bp', __name__, template_folder='templates', static_folder='static')


@Dash_bp.route('/Dashboard')
@login_required
def dashboard():
    """main drop page"""
    return render_template('dash.html')


@Dash_bp.route('/Dashboard/Data', methods=['GET'])
@login_required
def dash_data():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = ""
    try:
        res = cache.get('in_service')

        if not res:
            res = session.execute("SELECT allparts.id, DATE_FORMAT(allparts.create, '%M %D %Y'), parts.name, equipment.name, allparts.quantity FROM allparts, parts, equipment WHERE allparts.installed_in = equipment.id and allparts.part = parts.id and allparts.active = 1")
            res = res.fetchall()
            cache.set('in_service', res, 0)
        else:
            print("Found in cache")

        for row in res:
            print(row)
            data = data + '{"name": "' + str(row[2]) + '","installed": "'+ str(row[3]) +'", "create": "'+ str(row[1]) +'", "id": ' + str(row[0]) + \
                   ', "life": "N/A", "quantity": "'+str(row[4])+'"  },'

    except:
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = '{"data": [' + data[:-1] + ']}'
    print(result)
    session.close()
    return json.loads(result)

@Dash_bp.route('/Dashboard/Delete', methods=['POST'])
@login_required
def delete_part():
    """main drop page"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    id = data['id']
    key = "parts_installed_"

    try:
        res = session.execute("select distinct allparts.installed_in from allparts where allparts.id=:id", {'id': id})
        res = res.fetchall()

        for row in res:
            key = key+str(row[0])

        cache.delete('in_service')
        cache.delete(key)

        # reduce quantity, delete if now zero
        session.query(AllParts).filter(AllParts.id == id).update({'quantity': AllParts.quantity - int(data['quantity'])})
        part = session.query(AllParts).filter(AllParts.id == id).first()

        if int(part.quantity) == 0:
            session.query(AllParts).filter(AllParts.id == id).update({'active': 0, 'delete': time.strftime('%Y-%m-%d %H:%M:%S')})

        res = session.execute("select allparts.create, allparts.part from allparts where allparts.id=:id", {'id': id})

        for i in range(int(data['quantity'])):
            for row in res:
                session.execute("insert into failed values (default, :create, :part, NOW())",{'part':str(row[0]), 'create': str(row[1])})

        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Dash_bp.route('/Dashboard/Quantity', methods=['POST'])
@login_required
def part_quant():
    """main drop page"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    id = data['id']
    result = '{"quantity":'

    try:
        res = session.execute("select distinct allparts.quantity from allparts where allparts.id=:id", {'id': id})
        res = res.fetchall()

        for row in res:
            result += '"'+str(row[0])+'"}'

        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


    session.close()
    return json.loads(result)

