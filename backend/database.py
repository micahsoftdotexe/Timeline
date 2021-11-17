import mariadb as mdb
import sys
class Database():
    def __init__(self,url, username, password,name):
        try: 
            self.connection = mdb.connect(
                user = username,
                password = password,
                host = url,
                port = 3306,
                database = name,
                connect_timeout=1000,
                #wait_timeout=28800,
                #interactive_timeout=28800
            )
        except mdb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
        self.cursor = self.connection.cursor()