from flask import Blueprint, render_template, request
from flask import current_app as app
from flask_login import login_required
from supplier import Supplier
from sqlalchemy.orm import sessionmaker
from __init__ import db, cache
import json

Sup_bp = Blueprint('Sup__bp', __name__, template_folder='templates', static_folder='static')


@Sup_bp.route('/Suppliers')
@login_required
def supplier():
    """main login page"""
    return render_template('supplier.html')


@Sup_bp.route('/Suppliers/Data', methods=['GET'])
@login_required
def supplier_data():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = ""
    try:
        res = cache.get('all_suppliers')

        if not res:
            res = session.execute("select supplier.name, supplier.email, supplier.phone, supplier.id from supplier where supplier.active = 1")
            res = res.fetchall()
            cache.set('all_suppliers', res, 0)
        else:
            print("Found in cache")

        for row in res:
            data = data + '{"name": "' + str(row[0]) + '","email": "'+ str(row[1]) +'", "phone": "'+ str(row[2]) +'", "id": ' + str(row[3]) + ' },'

    except:
        session.close()
        json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = '{"data": [' + data[:-1] + ']}'
    print(result)
    session.close()
    return json.loads(result)


@Sup_bp.route('/Suppliers/Get', methods=['POST'])
@login_required
def supplier_get():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    id = data['id']
    data = ""
    key = "supplier_"+str(id)

    try:
        res = cache.get(key)

        if not res:
            res = session.execute("SELECT  supplier.name, supplier.email, supplier.phone, supplier.id from supplier where supplier.active = 1 and supplier.id = :id", {'id': id})
            res = res.fetchall()
            cache.set(key, res, 0)
        else:
            print("Found in cache")

        for row in res:
            data = data + '{"name": "' + str(row[0]) + '","email": "'+ str(row[1]) +'", "phone": "'+ str(row[2]) +'", "id": ' + str(row[3]) + ' },'

    except:
        session.close()
        json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = data[:-1]
    print(result)
    session.close()
    return json.loads(result)


@Sup_bp.route('/Suppliers/Delete', methods=['POST'])
@login_required
def supplier_delete():
    """main drop page"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    id = data['id']
    key = "supplier_" + str(id)

    try:
        cache.delete(key)
        cache.delete('all_suppliers')
        cache.delete('all_active_parts')
        session.query(Supplier).filter(Supplier.id == id).update({'active': 0})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Sup_bp.route('/Suppliers/Update', methods=['POST'])
@login_required
def supplier_update():
    """main drop page"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    id = data['id']
    key = "supplier_" + str(id)

    try:
        cache.delete(key)
        cache.delete('all_suppliers')
        cache.delete('all_active_parts')
        session.query(Supplier).filter(Supplier.id == id).update({'phone': str(data['phone']), 'email': str(data['email']), 'name': str(data['name'])})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

