import flask_login
from werkzeug.security import generate_password_hash
#from database import Database
class User(flask_login.UserMixin): 
    def __init__(self,username,first_name,last_name,password, role = 'Employee',  hashed = False, id = None):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.password = generate_password_hash(password) if (not hashed) else password 
        self.role = role
        self.id = id
    def set(self, database):
        database.cursor.execute("INSERT INTO user (username, first_name, last_name, password, role) VALUES (?, ?, ?, ?, ?);",
        (self.username, self.first_name, self.last_name, self.password, self.role)) 
        database.connection.commit()
        #print(cur.last_executed)
        return 1 
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)
    def to_json(self):
        return {
            'username': self.username,
            'firstName' : self.first_name,
            'lastName'  : self.last_name,
            'role': self.role,
            'id': self.id
        } 
    def getClockEntries(self,database):
        database.cursor.execute("SELECT * FROM clock_entries WHERE user_id=? ORDER BY clock_in_time ASC", (self.id,))
        return database.cursor.fetchall()
    
    def checkRole(self,role):
        if(self.role == 'admin' or self.role == role):
            return True
        else:
            return False
    @staticmethod
    def getById(id,database):
        database.cursor.execute(f"SELECT * FROM user WHERE id = {id}")
        if(database.cursor.arraysize >0 and database.cursor.arraysize<2): 
            user_array = database.cursor.fetchone()
            return User(user_array[0], user_array[1], user_array[2], user_array[3], user_array[4], True, user_array[5])
    @staticmethod
    def getByUsername(username,database):
        database.cursor.execute(f"SELECT * FROM user WHERE username=?;", (username,))
        if(database.cursor.arraysize >0 and database.cursor.arraysize<2): 
            user_array = database.cursor.fetchone()
            return User(user_array[0], user_array[1], user_array[2], user_array[3], user_array[4], True, user_array[5])   
        else:
            return -1