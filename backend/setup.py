from backend.database import Database
import json
import sys
from backend.user import User

database = None
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
def checkTables(tableName):
    f = open('./settings.json')
    settings = json.load(f)["database"]
    database_name = settings["database_name"]
    database.cursor.execute("SELECT count(*) FROM information_schema.TABLES WHERE (TABLE_SCHEMA = ?) AND (TABLE_NAME = ?)", (database_name, tableName))
    if(database.cursor.fetchone()[0] > 0):
        return True
    else:
        return False
def dropTables():
    if(checkTables('clock_entries')):
        database.cursor.execute("DROP TABLE clock_entries")
        database.connection.commit()
    if(checkTables('user')):
        database.cursor.execute("DROP TABLE user")
        database.connection.commit()
def migrate():
    #check if drop tables needed
    f = open('./settings.json')
    settings = json.load(f)["database"]
    database_name = settings["database_name"]
    dropTables()
    database.cursor.execute("CREATE TABLE `clock_entries` (`id` int(11) NOT NULL,`user_id` int(11) NOT NULL,`clock_in_time` datetime(1) NOT NULL,`clock_out_time` datetime DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
    database.cursor.execute("CREATE TABLE `user` (`username` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,`first_name` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,`last_name` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,`password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,`wage` decimal(10,2) DEFAULT NULL,`role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,`id` int(11) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
    database.cursor.execute("ALTER TABLE `clock_entries` ADD PRIMARY KEY (`id`), ADD KEY `user_id` (`user_id`);")
    database.cursor.execute("ALTER TABLE `user` ADD PRIMARY KEY (`id`);")
    database.cursor.execute("ALTER TABLE `clock_entries` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;")
    database.cursor.execute("ALTER TABLE `user` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38")
    database.cursor.execute("ALTER TABLE `clock_entries` ADD CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);")
    database.connection.commit()

def seedAdmin(username,password):
    admin = User(username, "admin", "admin", password, None, 'admin')
    admin.set(database)
    return True

def setup():
    if(database == None):
        connectDb()
    f = open('./settings.json', 'r+')
    json_file1 = json.load(f)
    settings = json_file1["database"]
    #print('out here')
    if settings['migrate'] == "true":
        #print('Here')
        migrate()
        username = json_file1["defaults"]['adminUser']["username"]
        #print(username)
        password = json_file1["defaults"]["adminUser"]["password"]
        seedAdmin(username,password)
        json_file1["database"]['migrate'] = "false"
        f.seek(0)
        json.dump(json_file1, f)
        f.truncate()
        f.close()


    return True   

#setup()