from flask import Blueprint, render_template, request, redirect
from flask import current_app as app
from flask_login import login_required, login_user, current_user
from sqlalchemy.orm import sessionmaker
from __init__ import db, cache
import json
from user import User
from werkzeug.security import generate_password_hash

Admin_bp = Blueprint('Admin__bp', __name__, template_folder='templates', static_folder='static')


@Admin_bp.route('/Admin')
@login_required
def admin():
    """main login page"""
    return render_template('admin.html')


@Admin_bp.route('/Admin/Create/Equipment' , methods=['POST'])
@login_required
def create_equipment():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])

    try:
        cache.delete('all_equipment')

        session.execute("INSERT INTO equipment VALUES (default ,:name, :year, 1)", {'name': data['name'], 'year': data['year']})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Admin_bp.route('/Admin/Create/Location', methods=['POST'])
@login_required
def create_location():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])

    try:
        cache.delete('all_locations')

        session.execute(
            "INSERT INTO locations VALUES (default ,:name, 1)", {'name': data['name']})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Admin_bp.route('/Admin/Create/Supplier', methods=['POST'])
@login_required
def create_supplier():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])

    try:
        cache.delete('all_suppliers')

        session.execute(
            "INSERT INTO supplier VALUES (default ,:name, :email, :phone, 1)",
            {'name': data['name'], 'email': data['email'], 'phone': data['phone']})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Admin_bp.route('/Admin/Create/Part', methods=['POST'])
@login_required
def create_part():
    """ {name: $('#equipmentName').val(), year: $('#partSelect').val(), supplier: $('#partSelect2').val(),
          harvest: $('#partRadio1').is(":checked"), spraying:$('#partRadio2').is(":checked"),
              seeding: $('#partRadio3').is(":checked"), winter: $('#partRadio4').is(":checked")}"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])

    try:
        cache.delete('all_active_parts')

        session.execute('Insert into mlmodels values(default, :name, 0, 0, 0, 0, 0)',{'name': data['name']})

        res = session.execute('select max(id) from mlmodels')
        maxKey = 0

        for row in res:
            maxKey = row[0]

        session.execute("INSERT INTO parts VALUES (default ,:name, :supplier, :quantity, :location, 1, :harvest, :spraying, :seeding, :winter, :model)",
                        {'name': data['name'], 'supplier': data['supplier'], 'quantity': data['quantity'], 'location': data['location'],
                         'harvest': 1 if data['harvest'] else 0, 'spraying': 1 if data['spraying'] else 0, 'seeding': 1 if data['seeding'] else 0, 'winter': 1 if data['winter'] else 0,'model':maxKey})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Admin_bp.route('/Admin/Save/Changes', methods=['POST'])
@login_required
def save_changes():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])

    try:
        """update username"""
        if data['userName'] != "":
            session.query(User).filter(User.id == current_user.id).update({'email': data['userName']})

        """update name"""
        if data['name'] != "":
            session.query(User).filter(User.id == current_user.id).update({'name': data['name']})

        """update password"""
        if data['password'] != "":
            session.query(User).filter(User.id == current_user.id).update({'password': generate_password_hash(data['password'])})

        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Admin_bp.route('/Admin/Save/Deletion', methods=['GET'])
@login_required
def delete_user():
    print(current_user)
    Session = sessionmaker(bind=db.engine)
    session = Session()

    try:
        session.query(User).filter(User.id == current_user.id).update({'active': 0})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return redirect("/")


@Admin_bp.route('/Admin/Load', methods=['GET'])
@login_required
def info():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    user = '{"user": {"username": "'+current_user.name+'"}, '

    try:
        locations = '"locations": ['
        data = session.execute("SELECT distinct id, name from supplier where active = 1")

        for row in data:
            locations = locations+'{"id": '+str(row[0])+', "name": "'+str(row[1])+'"},'

        if locations[-1] != '[':
            locations = locations[:-1]

        locations = locations + '],'

        suppliers = '"suppliers": ['
        data = session.execute("SELECT distinct id, name from locations where active = 1")

        for row in data:
            suppliers = suppliers + '{"id": '+str(row[0])+', "name": "'+str(row[1])+'"},'

        if suppliers[-1] != "[":
            suppliers = suppliers[:-1]

        suppliers = suppliers + ']}'

        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    res = user+locations+suppliers
    print(res)
    return json.loads(res)


@Admin_bp.route('/Admin/ML', methods=['GET'])
@login_required
def enable_model():
    data = json.loads(request.form['sendData'])
    print(data)
    if None is None:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
    else:
        return redirect("/")
