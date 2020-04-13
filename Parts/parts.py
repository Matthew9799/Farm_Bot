from flask import Blueprint, render_template, request, send_from_directory, redirect
from flask import current_app as app
from flask_login import login_required
from __init__ import db, cache
from sqlalchemy.orm import sessionmaker
from parts import Parts
import os
from werkzeug.utils import secure_filename
from location import Location
from supplier import Supplier
from PIL import Image
import json

Parts_bp = Blueprint('Parts__bp', __name__, template_folder='template', static_folder='static')


@Parts_bp.route('/Parts')
@login_required
def parts():
    """main login page"""
    return render_template('items.html')


@Parts_bp.route('/Parts/Data', methods=['GET'])
@login_required
def get_parts():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = ""

    try:
        res = cache.get('all_active_parts')

        if not res:
            res = session.execute("SELECT parts.id, supplier.name, locations.name, parts.quantity, parts.name FROM parts, locations, supplier WHERE parts.location = locations.id and parts.supplier = supplier.id and parts.active = 1")
            res = res.fetchall()
            cache.set('all_active_parts', res, 0)
        else:
            print("Found in cache")

        for row in res:
            print(row)
            data = data + '{"name": "' + str(row[4]) + '","location": "'+ str(row[2]) +'", "quantity": "'+ str(row[3]) +'", "id": ' + str(row[0]) + \
                   ', "supplier": "'+ str(row[1]) +'"  },'

    except:
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = '{"data": [' + data[:-1] + ']}'
    print(result)
    session.close()
    return json.loads(result)


@Parts_bp.route('/Parts/Update', methods=['POST'])
@login_required
def update_parts():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    id = data['id']
    key = "part_" + str(id) + "_"

    try:
        cache.delete('all_active_parts')
        cache.delete(key)
        cache.delete('in_service')
        cache.delete("parts_installed_"+str(data['machine']))


        session.execute("INSERT INTO allparts VALUES (default ,:part, :machine, 0, :quant, 1, NOW(), null)",{'part': data['id'], 'machine': data['machine'], 'quant': data['quantity']})
        session.execute("UPDATE parts SET parts.quantity = parts.quantity - :quant where parts.id = :id",{'quant': data['quantity'], 'id': id})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Parts_bp.route('/Parts/Delete', methods=['POST'])
@login_required
def delete_parts():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    id = data['id']
    key = "part_" + str(id) + "_"

    try:
        cache.delete('all_active_parts')
        cache.delete(key)
        session.query(Parts).filter(Parts.id == id).update({'active': 0})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Parts_bp.route('/Parts/Get', methods=['POST'])
@login_required
def supplier_get():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    id = data['id']
    data = ""
    key = "part_"+str(id)+"_"

    try:
        res = cache.get(key)

        if not res:
            res = session.execute("SELECT parts.name, parts.quantity, parts.id from parts where parts.id = :id and parts.active = 1", {'id': id})
            res = res.fetchall()
            cache.set(key, res, 0)
        else:
            print("Found in cache")

        for row in res:
            data = data + '{"name": "' + str(row[0]) + '","quantity": "'+ str(row[1]) +'", "id": "'+ str(row[2]) +'" },'

    except:
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    result = data[:-1]
    print(result)
    session.close()
    return json.loads(result)


@Parts_bp.route('/Parts/Set', methods=['POST'])
@login_required
def supplier_set():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    data = json.loads(request.form['sendData'])
    key = "part_" + str(data['id']) + "_"

    try:
        cache.delete('all_active_parts')
        cache.delete(key)
        session.query(Parts).filter(Parts.id == data['id']).update({'quantity': data['quantity'], 'name': data['name']})
        session.commit()
    except:
        session.rollback()
        session.close()
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    session.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@Parts_bp.route('/Parts/Images/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/Parts/Upload/Image/<imageid>', methods=['POST'])
@login_required
def upload_file(imageid):
    file = request.files['file']
    print(imageid)

    if file.filename == '':
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    filename = secure_filename(file.filename)
    file.save(os.path.join(os.getcwd(),"Parts/old", filename))

    image = Image.open(os.path.join(os.getcwd(), "Parts/old", filename))
    image = image.convert('RGB')
    image.save(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], str(imageid)+'.jpg'), optimize=True)
    os.remove(os.path.join(os.getcwd(), "Parts/old", filename))

    return redirect("/Parts")


@app.route('/Parts/Delete/Image', methods=['POST'])
@login_required
def delete_image():
    data = json.loads(request.form['sendData'])
    os.remove(os.path.join(os.getcwd(),app.config['UPLOAD_FOLDER'], str(data['id'])+".jpg"))
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

