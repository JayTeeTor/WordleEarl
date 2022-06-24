from datetime import datetime
from re import S
from user import User
from secrets import randbelow
from tools.regex_helper import initDictionary
# from tools.regex_helper import isWord


class Wordle:
    def __init__(self, conn, game_mode):
        self.reset(conn, game_mode)

    def reset(self, conn, game_mode):  #spoiler/dm
        self.conn = conn
        self.players = {}
        self.start_time = datetime.now()
        self.game_state = 0
        self.game_id = 0  #Used with persistent data
        self.guess_limit = 5
        self.current_word = ""
        self.word_length = 0
        self.game_mode = game_mode
        self.modes_dict = {"spoiler": "spoiler", "dm": "dm"}
        self.valid_word_list = initDictionary()

    def startGame(self, len, user_id):

        user = User(self.conn, user_id)

        if (self.pendingPlayers()):
            if user_id in self.players:
                if (self.players[user_id].completed_guess):
                    raise Exception("user_won")
                raise Exception("user_exists")
            else:
                raise Exception("game_exists")

        self.reset(self.conn, self.game_mode)
        self.current_word = self.fetchWord(len)
        self.word_length = len
        self.game_state = 1
        self.players[user_id] = user

        if self.conn != False:
            self.newGameDB()
            self.addGamePlyr(user.getDBUserID(self.conn))

    def fetchWord(self, length):
        f = open(r"./bot/tools/words/words.txt", "r")
        lines = f.readlines()
        num_words = len(lines)
        choice = False
        while choice is False:
            choice = randbelow(num_words - 1)
            choice = lines[choice].strip()
            if len(choice) is length:
                if self.conn != False:
                    was_used = self.fetchPrevWord(choice)
                    if len(was_used) == 0:
                        print("CHOOSING: " + choice)
                        return choice
                else:
                    print("CHOOSING: " + choice)
                    return choice
            choice = False

    def joinGame(self, user_id):
        if not self.gameIsRunning():
            raise Exception("!game_exists")
        if self.playerExists(user_id):
            raise Exception("user_exists")

        user = User(self.conn, user_id)
        self.players[user_id] = user

        #TODO: TEST THIS!!
        if self.conn != False:
            self.addGamePlyrDB(user)

    #TODO: Ensure word is actually a word..
    def submitGuess(self, user_id, guess):

        if not self.gameIsRunning():
            raise Exception("!game_exists")

        if not self.playerExists(user_id):
            self.joinGame(user_id)

        current_user = self.players[user_id]

        if current_user.guess_count >= self.guess_limit:
            raise Exception("limit_reached")

        if current_user.completed_guess:
            raise Exception("completed")
        if guess in current_user.guesses:
            raise Exception("dupe_guess")

        if not guess in self.valid_word_list:
            raise Exception("!word")

        current_user.guesses.append(guess)
        current_user.guess_count += 1
        if self.conn != False:
            current_user.incrementGuessDB(self.conn, self.game_id)

        if guess == self.current_word:
            current_user.completed_guess = True
            if self.conn != False:
                current_user.incrementWinDB(self.conn, self.game_id)

    def playerExists(self, user_id):
        return True if user_id in self.players else False

    def gameIsRunning(self):
        return True if self.game_state else False

    def pendingPlayers(self):
        if (not self.game_state): return False  # No game running
        if (not len(self.players)):
            return False  #Players dont exist in the game
        players_pending = False

        for key in self.players.keys():
            if (not self.players[key].completed_guess):
                players_pending = True

        return players_pending

    def listPlayers(self):
        if (not len(self.players)): return False

        return self.players.keys()

    def currentPlayerInfo(self):
        if (not len(self.players)): return False
        if (not self.gameIsRunning()): return False

        payload = []
        for player in self.players.keys():
            tmp = []
            tmp.append(self.players[player].user_id)
            tmp.append(len(self.players[player].guesses))
            tmp.append(self.players[player].completed_guess)
            payload.append(tmp)

        return payload

    def guessMessageInfo(self, user_id):
        current_user = self.players[user_id]

        return {
            "user_id": user_id,
            "guesses": current_user.guesses,
            "target_word": self.current_word,
            "target_len": self.word_length
        }

    def cleanseWord(self, word):
        print("WORD IS " + word)
        word = str(word)
        if not isinstance(word, str):
            return "bad_word"

        if self.game_mode == self.modes_dict["spoiler"]:
            if not word[:2] == "||" or not word[len(word) - 2:] == "||":
                return "no_spoiler"
            elif len(word) - 4 != self.word_length:
                return "bad_length"
            else:
                word = word[2:]
                word = word[:len(word) - 2]
                return word

        else:
            if not len(word) is self.word_length:
                return "bad_length"
            else:
                return word

    def newGameDB(self):
        query = "INSERT INTO games (word, timestamp) VALUES (%s, NOW())"
        params = [self.current_word]
        result = self.conn.insert_query(query, params)

        query = "SELECT game_id FROM games ORDER BY game_id DESC LIMIT 1"
        params = []
        result = self.conn.select_query(query, params)
        self.game_id = result[0][0]

    def addGamePlyr(self, user_id):
        query = "INSERT INTO game_plyrs (game_id, user_id, guesses, completed) VALUES (%s, %s, 0, 0)"
        params = [self.game_id, user_id]
        self.conn.insert_query(query, params)

    def fetchPrevWord(self, word):
        query = "SELECT * FROM games WHERE word = %s"
        params = [word]

        result = self.conn.select_query(query, params)

        return result

    def addGamePlyrDB(self, user):
        query = "INSERT INTO game_plyrs (`game_id`, `user_id`, `guesses`, `completed`) VALUES (%s, %s, 0, 0)"
        params = [self.game_id, user.getDBUserID(self.conn)]
        self.conn.insert_query(query, params)

    #External Use
    def fetchPlyrInfo(self, user_id):
        if self.conn == False:
            return False

        user = User(self.conn, user_id)

        info = user.fetchStatsDB(self.conn)
        return False if info == False else info

    def fetchAllPlyrInfo(self, user_id):
        if self.conn == False:
            return False

        user = User(self.conn, user_id)
        info = user.fetchAllStatsDB(self.conn)
        return False if info == False else info
