class User:
    def __init__(self, conn, user_id):
        user_id = str(user_id)
        usr_tmp = user_id.split('#')
        self.user_id = usr_tmp[0]
        self.db_user_id = 0
        self.guess_count = 0
        self.guesses = []
        self.completed_guess = False

        if conn != False:
            self.dbInit(conn)
            self.updateLastPlaytime(conn)

    def dbInit(self, conn):
        user_info = self.getUserInfoDB(conn)
        if len(user_info) == 0:
            self.insertNewUserDB(conn)
        else:
            self.db_user_id = user_info[0][0]

    def getUserID(self):
        return self.user_id

    def setDBUserID(self, conn):

        query = "SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1"
        params = []
        user_id = conn.select_query(query, params)
        print(user_id)

        self.db_user_id = user_id[0][0]

    def getDBUserID(self, conn):

        return self.db_user_id

    def getUserInfoDB(self, conn):
        query = "SELECT * FROM users WHERE username = %s"
        params = [self.user_id]
        result = conn.select_query(query, params)
        return result

    def insertNewUserDB(self, conn):
        query = "INSERT INTO users (username, last_played) VALUES (%s, NOW())"
        params = [self.user_id]
        result = conn.insert_query(query, params)
        print(result)
        user_info = self.getUserInfoDB(conn)
        print(user_info)
        print(user_info[0][0])
        query = "INSERT INTO stats (user_id) VALUES (%s)"
        params = user_info[0][0]
        conn.insert_query(query, params)

        self.setDBUserID(conn)

        return result

    def incrementGuessDB(self, conn, game_id):
        query = "UPDATE game_plyrs SET guesses = guesses + 1 WHERE user_id = %s AND game_id = %s"
        params = [self.db_user_id, game_id]
        conn.update_query(query, params)

    def incrementWinDB(self, conn, game_id):
        query = "UPDATE game_plyrs SET completed = 1 WHERE user_id = %s AND game_id = %s"
        params = [self.db_user_id, game_id]
        conn.update_query(query, params)

    def updateLastPlaytime(self, conn):
        query = "UPDATE users SET last_played = NOW() WHERE user_id = %s"
        params = [self.db_user_id]
        conn.update_query(query, params)

    def fetchStatsDB(self, conn):
        query = "SELECT users.*, stats.count, stats.guess_sum, stats.completed_sum,  (stats.count - stats.completed_sum) AS loss_sum\
                FROM users\
                LEFT JOIN\
                    (SELECT user_id, COUNT(*) AS count, SUM(guesses) AS guess_sum, SUM(completed) AS completed_sum FROM game_plyrs GROUP BY user_id) AS stats ON users.user_id = stats.user_id\
                WHERE users.user_id = %s"

        params = [self.db_user_id]

        info = conn.select_query(query, params)

        return False if len(info) == 0 else info[0]

    def fetchAllStatsDB(self, conn):

        query = "SELECT users.*, stats.count, stats.guess_sum, stats.completed_sum,  (stats.count - stats.completed_sum) AS loss_sum\
                    FROM users\
                    LEFT JOIN\
                        (SELECT user_id, COUNT(*) AS count, SUM(guesses) AS guess_sum, SUM(completed) AS completed_sum FROM game_plyrs GROUP BY user_id) AS stats ON users.user_id = stats.user_id\
                    ORDER BY users.username"

        params = []

        info = conn.select_query(query, params)

        return False if len(info) == 0 else info
