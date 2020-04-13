from flask import Blueprint, render_template, redirect, request
from flask import current_app as app
from flask_login import login_required, logout_user, login_user, current_user
import json
from user import User

from __init__ import db, cache
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import time
from datetime import datetime
from datetime import timedelta
from banned import Banned

Index_bp = Blueprint('Index__bp', __name__, template_folder='templates', static_folder='static')


@Index_bp.route('/')
def login():
    """login page route."""
    logout_user()
    return render_template('index.html')


@Index_bp.route("/Logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect("/")


@Index_bp.route('/Authenticate', methods=['POST'])
def verifyuser():
    data = json.loads(request.form['sendData'])
    Session = sessionmaker(bind=db.engine)
    session = Session()
    count = 0
    f = '%Y-%m-%d %H:%M:%S'

    ip = session.execute("select count(1) from banned where banned.ipAddress =:addr", {'addr': request.remote_addr})

    for rows in ip:
        count = rows[0]

    if count == 0:
        try:
            session.execute("insert into banned values (default, :addr, 0,0, null, 0, 1)",
                            {'addr': request.remote_addr})
            session.commit()
        except:
            session.rollback()
            session.close()
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    attempts = session.execute("select banned.attempts, banned.permaBan, banned.lockoutStart from banned where banned.ipAddress = :addr", {'addr': request.remote_addr})
    minute_quant = 0
    perma_ban = 0
    lockout_start = None

    for rows in attempts:
        minute_quant = rows[0]
        perma_ban = rows[1]
        lockout_start = rows[2]

    if minute_quant < 20 and not perma_ban and ((lockout_start and datetime.strptime(str(lockout_start), f) +
                                                 timedelta(minutes=10) < datetime.now()) or not lockout_start):
        if data['name'] is not "" and data['code'] is not "" and data['code'] == "YOUR SECRET CODE":
            try:
                session.execute(
                    "Insert into users values (DEFAULT, :nme, :email, :password, (SELECT NOW()), (SELECT NOW()), 0, (SELECT NOW()), 1)",
                    {'nme': data['name'], 'email': data['username'],
                     'password': generate_password_hash(data['password'])})

                session.commit()
            except:
                session.rollback()
                session.close()
                return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

        res = User.query.filter_by(email=data['username'], active=1).first()

        if res and res.check_password(password=data['password']):
            login_user(res)
            try:
                session.query(User).filter(User.id == current_user.id).update(
                {'last_login': time.strftime('%Y-%m-%d %H:%M:%S'), 'failed_attempt': 0})
                session.query(Banned).filter(Banned.ipAddress == request.remote_addr).update(
                {'attempts': 0, 'weeklyAttempts': 0, 'lockoutStart': None})
                session.commit()
            except:
                session.rollback()
                session.close()
                return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

            session.close()
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        elif res and not res.check_password(password=data['password']):
            try:
                session.query(User).filter(User.id == res.id).update(
                {'last_attempt': time.strftime('%Y-%m-%d %H:%M:%S'), 'failed_attempt': User.failed_attempt + 1})
                session.query(Banned).filter(Banned.ipAddress == request.remote_addr).update(
                {'attempts': Banned.attempts + 1, 'weeklyAttempts': Banned.weeklyAttempts + 1, 'lockoutStart': None})

                session.commit()
            except:
                session.rollback()
                session.close()
                return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

            session.close()
            return json.dumps({'success': False}), 401, {'ContentType': 'application/json'}
        else:
            try:
                session.query(Banned).filter(Banned.ipAddress == request.remote_addr).update(
                    {'attempts': Banned.attempts + 1, 'weeklyAttempts': Banned.weeklyAttempts + 1, 'lockoutStart': None})
                session.commit()
            except:
                session.rollback()
                session.close()
                return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

            session.close()
            return json.dumps({'success': False}), 401, {'ContentType': 'application/json'}
    else:
        if not lockout_start and (minute_quant >= 20):
            try:
                session.execute("update banned set lockoutStart = NOW() where banned.ipAddress =:addr",{'addr': request.remote_addr})
                session.commit()
            except:
                session.rollback()
                session.close()
                return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

        session.close()
        return json.dumps({'Banned': True}), 401, {'ContentType': 'application/json'}
