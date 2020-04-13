from flask import Blueprint, render_template, request
from flask import current_app as app
from flask_login import login_required
import json
from location import Location
from sqlalchemy.orm import sessionmaker
from __init__ import db, cache

Locat_bp = Blueprint('Locat__bp', __name__, template_folder='templates', static_folder='static')


@Locat_bp.route('/Locations')
@login_required
def equipment():
    """main login page"""
    return render_template('location.html')


@Locat_bp.route('/Locations/Data', methods=['GET'])
@login_required
def location_data():
    """main drop page"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = ""
    try:
        res = cache.get('all_locations')

        if not res:
            res = session.execute("select locations.name, locations.id from locations where locations.active = 1")
            res = res.fetchall()
            cache.set('all_locations', res, 0)
        else:
            print("Found in cache")

        for row in res:
            data = data+'{"name": "'+str(row[0])+'", "id": '+str(row[1])+' },'

    except:
        session.close()
        json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = '{"data": ['+data[:-1]+']}'
    print(result)
    session.close()
    return json.loads(result)


@Locat_bp.route('/Locations/Delete', methods=['POST'])
@login_required
def location_delete():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    index = data['id']
    key = "location_" + str(index)
    try:
        cache.delete('all_locations')
        cache.delete(key)
        cache.delete('all_active_parts')
        session.query(Location).filter(Location.id == index).update({'active': 0})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    print("Successful Delete Location")
    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Locat_bp.route('/Locations/Update', methods=['POST'])
@login_required
def location_update():
    """main drop page"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    index = data['id']
    key = "location_" + str(index)
    try:
        cache.delete('all_locations')
        cache.delete(key)
        cache.delete('all_active_parts')
        session.query(Location).filter(Location.id == index).update({'name': str(data['name'])})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    print("Successful Update Location")
    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Locat_bp.route('/Locations/Get', methods=['POST'])
@login_required
def location_get():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    id = data['id']
    data = ""
    key = "location_"+str(id)

    try:
        res = cache.get(key)

        if not res:
            res = session.execute("SELECT locations.name, locations.id from locations where locations.active = 1 and locations.id = :id",{'id': id})
            res = res.fetchall()
            cache.set(key, res, 0)
        else:
            print("Found in cache")

        for row in res:
            data = data + '{"name": "' + str(row[0])+'", "id": '+str(row[1])+' },'

    except:
        session.close()
        json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = data[:-1]
    print(result)
    session.close()
    return json.loads(result)