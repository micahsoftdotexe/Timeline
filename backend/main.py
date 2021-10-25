from flask import Flask, jsonify, json, request
import flask_login
from flask_login import login_required
import json
from flask_cors import CORS
from flask_login.utils import logout_user
import os
from werkzeug.security import check_password_hash
from user import User
from database import Database
import datetime
database = None
login_manager = flask_login.LoginManager()
app = Flask(__name__)

def connectDb():
    f = open('../settings.json')
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

# @app.route('/hello')
# @login_required
# def hello():
#     user = User.getById(1,database)
#     userDict = {
#         'username': user.username,
#         'firstName' : user.first_name,
#         'lastName'  : user.last_name,
#         'password': user.password,
#         'role': user.role,
#         'id': user.id
#     }
#     return jsonify(userDict)

@app.route('/register', methods=['POST'])
def register():
    user = User(request.json["username"], request.json["first_name"], request.json["last_name"], request.json["password"])
    #print(user.password)
    user.set(database)
    return "200"

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    user = User.getByUsername(username,database)
    if(user != -1): 
        if(check_password_hash(user.password,request.json['password'])):
            flask_login.login_user(user)
            return jsonify(user.to_json()) 
        else:
            return jsonify({"status": 401,
                "reason": "Username or Password Error"})
    else:
        return jsonify({"status": 401,
            "reason": "Username or Password Error"})

@app.route('/logout')
def logout():
    logout_user()
    return jsonify({"status":200,})

@app.route('/get-current-user')
@login_required
def getUser():
    return (flask_login.current_user.to_json())

#given a user. Test if the user can clock in or needs to clock out
def testClockIn(user):
    lastentry = user.getClockEntries(database)[-1]
    #print(lastentry)
    if(lastentry[-1] == None):
        return False
    else:
        return True

@app.route('/clockin')
@login_required
def clockIn():
    user = flask_login.current_user
    if(testClockIn(user)):
        database.cursor.execute("INSERT INTO clock_entries (user_id, clock_in_time) VALUES (?, CURRENT_TIMESTAMP);",(user.id,))
        database.connection.commit()
        return jsonify({"status":200, "data": "Clocked in"})   
    else:
        return jsonify({"status":200, "data": "Cannot clock in"})

@app.route('/clockout')
@login_required
def clockOut():
    user = flask_login.current_user
    if(not testClockIn(user)):
        lastid = user.getClockEntries(database)[-1][0]
        database.cursor.execute("UPDATE clock_entries SET clock_out_time = CURRENT_TIMESTAMP WHERE id = ?;",(lastid,))
        database.connection.commit()
        return jsonify({"status":200, "data": "Clocked out"})   
    else:
        return jsonify({"status":200, "data": "Cannot clock out"})

@app.route('/report/<userId>', methods=['GET','POST'])
@login_required
def report(userId):
    if(flask_login.current_user.checkRole('manager')):
        #calculate start and stop dates
        tomorrow = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.datetime.min.time())
        last_week = (tomorrow - datetime.timedelta(weeks=1)) - datetime.timedelta(days=1)
        database.cursor.execute("SELECT * FROM clock_entries WHERE user_id=? AND clock_in_time > ? AND (clock_out_time < ? OR clock_out_time IS NULL)", (userId, last_week.strftime("%Y-%m-%d %H:%M:%S"), tomorrow.strftime("%Y-%m-%d %H:%M:%S"),))
        entries = database.cursor.fetchall()
        response = {}
        total_hours = 0
        for entry in entries:
            if(entry[-1] != None):
                total_time = entry[-1]-entry[-2]
                # print(entry[0])
                # print(total_time.total_seconds()/3600)
                total_hours += total_time.total_seconds()/3600
            else:
                print('here')
                # if(response.has_key('unfinished')):
                if('unfinished' in response):
                   response['unfinished'].append(entry[-2])
                else:
                    response['unfinished'] = [entry[-2]]
        response['total_hours'] = total_hours
        if(flask_login.current_user.wage != None):
            response['wage'] = round(flask_login.current_user.wage*total_hours,2)
        
                 
        return jsonify(response)
    else:
        return jsonify({"status":401})

@app.route('/delete/<recordId>', methods=['DELETE'])
@login_required
def deleteClock(recordId):
    database.cursor.execute("DELETE FROM clock_entries WHERE id=?",(recordId,))
    database.cursor.commit()
    return 1






def start_server():
    if database == None:
        connectDb()
    CORS(app)
    app.secret_key = os.urandom(24)
    login_manager.init_app(app)
    app.run(debug=True)



if __name__ == "__main__":

    #app = Flask(__name__)
    start_server()
    #print('here')