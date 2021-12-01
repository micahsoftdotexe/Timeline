from flask import Flask, jsonify, json, request
import flask_login
from flask_login import login_required
import json
from flask_cors import CORS
from flask_login.utils import logout_user
import os
from werkzeug.security import check_password_hash
from backend.user import User
from backend.database import Database
import datetime
database = None
login_manager = flask_login.LoginManager()
app = Flask(__name__)

def connectDb():
    f = open('./settings.json')
    settings = json.load(f)["database"]
    #load database settings from json settings file
    url = settings["url"]
    username = settings["username"]
    password = settings["password"]
    database_name = settings["database_name"]
    #connect to db
    global database
    database = Database(url,username,password,database_name)
    

@login_manager.user_loader
def load_user(id):
    return User.getById(id,database)

@app.route('/hello')
#@login_required
def hello():
    return 'hello'

@app.route('/register', methods=['POST'])
def register():
    if("username" in request.json and "first_name" in request.json and "last_name" in request.json and "password" in request.json):
        user = User(request.json["username"], request.json["first_name"], request.json["last_name"], request.json["password"])
        #print(user.password)
        user.set(database)
        return jsonify(True)
    else:
        return app.response_class(status=400,
                                  mimetype='application/json')

@app.route('/login', methods=['POST'])
def login():
    if('username' in request.json and 'password' in request.json):
        username = request.json['username']
        user = User.getByUsername(username,database)
        if(user != False): 
            if(check_password_hash(user.password,request.json['password'])):
                flask_login.login_user(user)
                return jsonify(user.to_json()) 
            else:
                # return jsonify({"status": 401,
                #     "reason": "Username or Password Error"})
                return app.response_class("Username or Password Error",
                                    status=401,
                                    mimetype='application/json')
        else:
            # return jsonify({"status": 401,
            #     "reason": "Username or Password Error"})
            return app.response_class("Username or Password Error",
                                    status=401,
                                    mimetype='application/json')
    else:
        return app.response_class(status=400,
                                  mimetype='application/json')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(True)

@app.route('/check-login')
def check_login():
    #print(flask_login.current_user.is_anonymous)
    return (jsonify(not flask_login.current_user.is_anonymous))

#given a user. Test if the user can clock in or needs to clock out
def testClockIn(user):
    if user.getClockEntries(database):
        lastentry = user.getClockEntries(database)[-1]
        #print(lastentry)
        if(lastentry[-1] == None):
            return False
        else:
            return True
    else:
        return True

@app.route('/clockin')
@login_required
def clockIn():
    user = flask_login.current_user
    if(testClockIn(user)):
        database.cursor.execute("INSERT INTO clock_entries (user_id, clock_in_time) VALUES (?, CURRENT_TIMESTAMP);",(user.id,))
        database.connection.commit()
        return jsonify("Clocked In")   
    else:
        return app.response_class("Connot Clock In",
                                  status=401,
                                  mimetype='application/json')

@app.route('/clockout')
@login_required
def clockOut():
    user = flask_login.current_user
    if(not testClockIn(user)):
        lastid = user.getClockEntries(database)[-1][0]
        database.cursor.execute("UPDATE clock_entries SET clock_out_time = CURRENT_TIMESTAMP WHERE id = ?;",(lastid,))
        database.connection.commit()
        return jsonify("Clocked In")
        #return jsonify({"status":200, "data": "Clocked out"})   
    else:
        return app.response_class("Connot Clock Out",
                                  status=401,
                                  mimetype='application/json')

@app.route('/report/<userId>', methods=['GET','POST'])
@login_required
def report(userId):
    if(flask_login.current_user.checkRole('manager')):
        #calculate start and stop dates
        response = {}
        tomorrow = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.datetime.min.time())
        last_week = (tomorrow - datetime.timedelta(weeks=1)) - datetime.timedelta(days=1)
        response['start_time'] = last_week
        response['end_time'] = tomorrow
        database.cursor.execute("SELECT * FROM clock_entries WHERE user_id=? AND clock_in_time > ? AND (clock_out_time < ? OR clock_out_time IS NULL)", (userId, last_week.strftime("%Y-%m-%d %H:%M:%S"), tomorrow.strftime("%Y-%m-%d %H:%M:%S"),))
        entries = database.cursor.fetchall()
        total_hours = 0
        response['unfinished'] = []
        for entry in entries:
            if(entry[-1] != None):
                total_time = entry[-1]-entry[-2]
                total_hours += total_time.total_seconds()/3600.0
            else:
                if('unfinished' in response):
                   response['unfinished'].append(entry[-2])
                else:
                    response['unfinished'] = [entry[-2]]
        response['total_hours'] = total_hours
        response['wage'] = "none"
        if(flask_login.current_user.wage != None):
            response['wage'] = str(round(float(flask_login.current_user.wage)*total_hours,2))
        
                 
        return jsonify(response)
    else:
        return app.response_class("No report",
                                  status=401,
                                  mimetype='application/json')

@app.route('/delete/<recordId>', methods=['DELETE'])
@login_required
def deleteClock(recordId):
    database.cursor.execute("DELETE FROM clock_entries WHERE id=?",(recordId,))
    database.connection.commit()
    return jsonify("Deleted record")






def start_server():
    from waitress import serve
    if database == None:
        connectDb()
    CORS(app, supports_credentials=True)
    app.secret_key = os.urandom(24)
    login_manager.init_app(app)
    app.run(debug=True, host="0.0.0.0")
    #serve(app, host = "0.0.0.0", port=8080)



if __name__ == "__main__":

    #app = Flask(__name__)
    start_server()
    #print('here')