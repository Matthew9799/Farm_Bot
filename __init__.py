from flask import Flask, redirect, send_from_directory
from flask_login import LoginManager

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy import Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
import os
import memcache
import time
from flaskthreads import AppContextThread
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

db = SQLAlchemy()
cache = memcache.Client(['localhost:11211'], debug=1)

import app

login_manager = LoginManager()
Base = declarative_base()

from Index import routes
from user import User


from banned import Banned
from allParts import AllParts
from parts import Parts
from supplier import Supplier
from location import Location
from equipmnt import Equipment
from mlmodel import MlModel
from failed import Failed


def create_app():
    appl = Flask(__name__, static_folder=os.path.abspath(''))
    appl.debug = True

    appl.secret_key = ""
    appl.config['SQLALCHEMY_DATABASE_URI'] = ''
    appl.config['UPLOAD_FOLDER'] = "Parts/static/"

    db.init_app(appl)
    login_manager.init_app(appl)

    with appl.app_context():
        db.create_all()
        Base.metadata.create_all(db.engine)

        global session


        from Error import error_routes
        from Admin import admin
        from Dashboard import dash
        from Equipment import equipment
        from Parts import parts
        from Locations import locations
        from Supplier import supplier


        appl.register_blueprint(routes.Index_bp)
        appl.register_blueprint(error_routes.Error_bp)
        appl.register_blueprint(dash.Dash_bp)
        appl.register_blueprint(admin.Admin_bp)
        appl.register_blueprint(equipment.Equip_bp)
        appl.register_blueprint(parts.Parts_bp)
        appl.register_blueprint(locations.Locat_bp)
        appl.register_blueprint(supplier.Sup_bp)

        AppContextThread(target=timer_jobs).start()

        return appl


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id, active=1).first()


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    print(user_id)

    user = User.query.filter_by(id=user_id, active=1).first()
    print(user)
    if user:
        return user
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    print("unauthorized")
    return redirect("/")

def timer_jobs():
    counter = 0
    dailyEmail = False
    shouldEmail = False

    while 1:
        time.sleep(60)
        now = datetime.now()

        Session = sessionmaker(bind=db.engine)
        session = Session()

        try:
            session.execute("update banned set banned.attempts = 0")

            if counter == 10080:
                session.execute("update banned set banned.permaBan = CASE when banned.weeklyAttempts > 500 or banned.permaBan = 1 then 1 else 0")
                session.execute("update banned set banned.weeklyAttempts = 0")
                session.execute("optimize table allparts")
                session.execute("optimize table banned")
                session.execute("optimize table equipment")
                session.execute("optimize table locations")
                session.execute("optimize table parts")
                session.execute("optimize table supplier")
                session.execute("optimize table users")
                counter = 0

            if now.hour == 7 and not dailyEmail:
                dailyEmail = True
                parts = session.execute("select parts.name, parts.quantity, supplier.name, supplier.phone, supplier.email from parts left join supplier on parts.supplier = supplier.id where parts.quantity < 5 order by parts.quantity")
                users = session.execute("select users.name, users.email from users where users.active = 1")

                try:
                    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    s.ehlo()
                    s.login('', '')

                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = "Low Parts"
                    msg['From'] = ""
                    msg['To'] = ""

                    html = '<!DOCTYPE html><html><head><style>table {'+ \
                           'font-family: arial, sans-serif;border-collapse: collapse;width: 100%;}td, th {border: 1px solid #dddddd;'+ \
                           'text-align: left;padding: 8px;}tr:nth-child(even) {background-color: #dddddd;}</style></head><body><h2>Parts</h2>'+ \
                           '<table><tr><th>Part Name</th><th>Quantity</th><th>Supplier Name</th><th>Supplier Phone</th><th>Supplier Email</th></tr>'

                    for part in parts:
                        shouldEmail = True
                        html += '<tr><td>'+str(part[0])+'</td><td>'+str(part[1])+'</td><td>'+str(part[2])+'</td><td>'+str(part[3])+'</td><td>'+str(part[4])+'</td></tr>'

                    html += '</table></body></html>'
                    part1 = MIMEText(html, 'html')
                    msg.attach(part1)

                    for people in users and shouldEmail:
                        s.sendmail("", str(people[1]), msg.as_string())

                    s.quit()
                except:
                    print("fail")


            if now.hour == 6 and dailyEmail:
                shouldEmail = False
                dailyEmail = False

            session.commit()
            counter += 1
        except:
            session.rollback()
            print("Issues purging banned")

        session.close()

