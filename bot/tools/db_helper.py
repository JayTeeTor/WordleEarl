import pymysql


class DBHelper():
    def __init__(self, db_host, db_uname, db_pass, db_schema,
                 db_port):  #Binds self to object attributes

        #TODO: Prepare for fresh databse, auto-create schemas and tables in that case
        #Open connection to db
        self.db = pymysql.connect(host=db_host,
                                  user=db_uname,
                                  password=db_pass,
                                  database=db_schema,
                                  port=db_port)

        self.cursor = self.db.cursor()

        self.dict_cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def select_query(self, query, params=False):
        query = query
        if params is not False:
            params = params
        try:
            self.db.ping(True)
            if params is False:
                self.cursor.execute(query)
            if params is not False:
                self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            return result
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False

    def select_query_dict(self, query, params=False):
        query = query
        if params is not False:
            params = params
        try:
            self.db.ping(True)
            if params is False:
                self.dict_cursor.execute(query)
            if params is not False:
                self.dict_cursor.execute(query, params)
            result = self.dict_cursor.fetchall()
            return result
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False

    def update_query(self, query, params=False):
        query = query
        if params != False:
            params = params
        try:
            self.db.ping(True)
            if params == False:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            self.db.commit()

        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            print(query)
            print(params)
            return False

    def insert_query(self, query, params=False):
        query = query
        if params != False:
            params = params
        try:
            self.db.ping(True)
            if params == False:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            self.db.commit()
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            print(query)
            print(params)
            return False

    def rowCount(self):
        return self.cursor.rowcount

    def closeDB(self):
        self.db.close()
