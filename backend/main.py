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
database = None
login_manager = flask_login.LoginManager()
app = Flask(__name__)

def connectDb():
    f = open('settings.json')
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
@login_required
def hello():
    user = User.getById(1,database)
    userDict = {
        'username': user.username,
        'firstName' : user.first_name,
        'lastName'  : user.last_name,
        'password': user.password,
        'role': user.role,
        'id': user.id
    }
    return jsonify(userDict)

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
    print(lastentry[-1])
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











if __name__ == "__main__":

    #app = Flask(__name__)
    if database == None:
        connectDb()
    CORS(app)
    app.secret_key = os.urandom(24)
    login_manager.init_app(app)
    app.run(debug=True)
    #print('here')