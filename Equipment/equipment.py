from flask import Blueprint, render_template, request
from flask import current_app as app
from flask_login import login_required
from __init__ import db, cache
from sqlalchemy.orm import sessionmaker
from equipmnt import Equipment
from allParts import AllParts
import json

Equip_bp = Blueprint('Equip__bp', __name__, template_folder='templates', static_folder='static')


@Equip_bp.route('/Equipment')
@login_required
def equipment():
    """main login page"""
    return render_template('equipment.html')


@Equip_bp.route('/Equipment/Data', methods=['GET'])
@login_required
def equipment_data():
    """main drop page"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = ""
    try:
        res = cache.get('all_equipment')

        if not res:
            res = session.execute("select equipment.name, equipment.year, equipment.id from equipment where equipment.active = 1")
            res = res.fetchall()
            cache.set('all_equipment', res, 0)
        else:
            print("Found in cache")

        for row in res:
            data = data + '{"name": "' + str(row[0]) + '","year": ' + str(row[1]) + ', "id": ' + str(row[2]) + ' },'

    except:
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = '{"data": [' + data[:-1] + ']}'
    print(result)
    session.close()
    return json.loads(result)


@Equip_bp.route('/Equipment/Parts', methods=['POST'])
@login_required
def equipment_parts():
    """main drop page"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    info = json.loads(request.form['sendData'])
    id = info['id']
    data = ""
    key = "parts_installed_"+str(id)

    try:
        res = cache.get(key)

        if not res:
            res = session.execute("SELECT distinct allparts.id, parts.name from allparts, parts, equipment where allparts.installed_in = :id and allparts.part = parts.id and allparts.active = 1", {'id':id})
            res = res.fetchall()
            cache.set(key, res, 0)
        else:
            print("Found in cache")

        for row in res:
            data = data + '{"name": "' + str(row[1]) + '","life": "N/A" },'

        print(data)

    except:
        print("error")
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = '{"data": [' + data[:-1] + ']}'
    print(result)
    session.close()
    return json.loads(result)


@Equip_bp.route('/Equipment/Get', methods=['POST'])
@login_required
def get_equipment():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    info = json.loads(request.form['sendData'])
    id = info['id']
    data = ""
    key = "equipment_" + str(id)

    try:
        res = cache.get(key)

        if not res:
            res = session.execute("SELECT equipment.name, equipment.year from equipment where equipment.id =:id and equipment.active = 1",{'id': id})
            res = res.fetchall()
            cache.set(key, res, 0)
        else:
            print("Found in cache")

        for row in res:
            data = data + '{"name": "' + str(row[0]) + '","year": "'+str(row[1])+'" },'

        print(data)

    except:
        print("error")
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = '{"data": [' + data[:-1] + ']}'
    print(result)
    session.close()
    return json.loads(result)


@Equip_bp.route('/Equipment/Update', methods=['POST'])
@login_required
def update_equipment():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    info = json.loads(request.form['sendData'])
    id = info['id']
    key = "equipment_" + str(id)

    try:
        cache.delete(key)
        cache.delete('all_equipment')
        cache.delete('in_service')
        session.query(Equipment).filter(Equipment.id == id).update({'name': info['name'], 'year': info['year']})
        session.commit()
    except:
        print("error")
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


@Equip_bp.route('/Equipment/Delete', methods=['POST'])
@login_required
def delete_equipment():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    info = json.loads(request.form['sendData'])
    id = info['id']
    data = ""
    key = "equipment_" + str(id)

    try:
        cache.delete(key)
        cache.delete('all_equipment')
        cache.delete('in_service')
        session.query(Equipment).filter(Equipment.id == id).update({'active': 0})
        session.commit()
    except:
        print("error")
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


