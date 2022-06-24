from posixpath import split
import discord
import os
from dotenv import load_dotenv
from wordle import Wordle
from tools.regex_helper import msgMatcher
from tools.db_helper import DBHelper
from tools.dialogue import Dialogue
import traceback

#LOAD ENV VARS
load_dotenv()

#DBCONN
db_uname = os.getenv('DB_UNAME')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_port = int(os.getenv('DB_PORT'))
db_schema = os.getenv('db_schema')
try:
    conn = DBHelper(db_host, db_uname, db_pass, db_schema, db_port)
except Exception as e:
    print(e)
    conn = False

#GAME SETUP & DISCORD CONN
wordle = Wordle(
    conn, "spoiler")  # (db connection, 1=spoiler_tag channel-mode / 2=dm mode)
dialogue = Dialogue(True)
client = discord.Client()

bot_name = "@WordleEarl"


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    response_msg = "err"
    if client.user in message.mentions or message.content.startswith(
            "!"):  #User mentioned us
        #Remove our mention from the message

        msg = message.content
        if (msg.strip()[0] == "!"):
            msg = msg[1:]
        else:
            msg = msg.split(" ")
            msg.pop(0)
            msg = ' '.join(msg)

        msg = msg.lower()
        #Begin Matching

        #Start a new game
        if (msgMatcher("START_GAME_REGEX", msg)):

            try:
                response_msg = dialogue.retrieveDialogue("starting_game")
                word_len = int(msg[2])
                wordle.startGame(word_len, message.author)

            except ValueError:
                print("Third argument was not a number! (`sg[num]l`)")
                response_msg = dialogue.retrieveDialogue("unknown")
            except Exception as e:
                if (str(e) == "user_won"):
                    response_msg = dialogue.retrieveDialogue(
                        "already_won_start")
                elif (str(e) == "user_exists"):
                    response_msg = dialogue.retrieveDialogue("already_joined")

                elif (str(e) == "game_exists"):
                    response_msg = dialogue.retrieveDialogue(
                        "already_won_start")
                    response_msg += "\n\n"
                    response_msg += "~~Either !guess or !join to begin~~"
                else:
                    print(e)
                    print(get_traceback(e))
                    response_msg = dialogue.retrieveDialogue("server_err")

        elif (msgMatcher("JOIN_GAME_REGEX", msg)):
            try:
                wordle.joinGame(message.author)
                response_msg = dialogue.retrieveDialogue("joining_game")
            except Exception as e:
                if (str(e) == "!game_exists"):
                    response_msg = dialogue.retrieveDialogue("!game_exists")
                if (str(e) == "user_exists"):
                    response_msg = dialogue.retrieveDialogue(
                        "already_won_join")
                else:
                    print(e)

        elif (msgMatcher("PLYR_GUESS_REGEX", msg)):
            msg_list = msg.split(" ")
            cleansed_word = wordle.cleanseWord(msg_list[1])
            if not wordle.gameIsRunning():

                response_msg = dialogue.retrieveDialogue("!game_exists")
            elif cleansed_word in ["bad_word", "no_spoiler", "bad_length"]:
                if cleansed_word == "bad_length":
                    response_msg = dialogue.retrieveDialogue(
                        "incorrect_len") + str(wordle.word_length)
                elif cleansed_word == "no_spoiler":
                    response_msg = dialogue.retrieveDialogue("spoiler_missing")
                    response_msg += "\n\n"
                    response_msg += "Surround your guess with `||word||` characters!"
                else:
                    print(wordle.cleanseWord(cleansed_word))
                    response_msg = "OOPS! Something went wrong :^("

            else:
                try:
                    result = wordle.submitGuess(message.author, cleansed_word)

                    response_msg = dialogue.constructGuessMessage(
                        wordle.guessMessageInfo(message.author))
                    # response_msg = "Guess registered"
                except Exception as e:
                    if (str(e) == "!game_exists"):
                        response_msg = dialogue.retrieveDialogue(
                            "!game_exists")
                    elif (str(e) == "limit_reached"):
                        response_msg = dialogue.retrieveDialogue(
                            "limit_reached")
                    elif (str(e) == "completed"):
                        response_msg = dialogue.retrieveDialogue(
                            "already_won_guess")

                    elif (str(e) == "dupe_guess"):
                        response_msg = dialogue.retrieveDialogue("dupe_guess")
                    elif (str(e) == "!word"):
                        response_msg = dialogue.retrieveDialogue(
                            "invalid_word")
                    else:
                        print(e)
                        print(get_traceback(e))
                        response_msg = dialogue.retrieveDialogue("server_err")

        elif (msgMatcher("RUN_CHECK_REGEX", msg)):
            print(wordle.gameIsRunning())
            print(wordle.game_state)
            response_msg = "response"

        elif (msgMatcher("PLYR_CHECK_REGEX", msg)):
            if not wordle.gameIsRunning():
                response_msg = dialogue.retrieveDialogue("!game_exists")
            else:
                response_msg = "```"
                response_msg += dialogue.constructCurrentPlyrsTbl(
                    wordle.currentPlayerInfo())
                response_msg += "```"

        elif (msgMatcher("HELP_REGEX", msg)):
            response_msg = dialogue.helpMenu()

        elif (msgMatcher("STATS_REGEX", msg)):
            if msg == "leaderboard":
                user_info = wordle.fetchAllPlyrInfo(message.author)
                if user_info == False:
                    response_msg = ":face_with_hand_over_mouth: NO PD :face_with_hand_over_mouth: "
                else:
                    response_msg = "```"
                    response_msg += dialogue.constructAllPlyrStatMessage(
                        user_info)
                    response_msg += "```"

            else:
                user_info = wordle.fetchPlyrInfo(message.author)
                if user_info == False:
                    response_msg = ":face_with_hand_over_mouth: NO PD :face_with_hand_over_mouth: "
                else:
                    response_msg = "```"
                    response_msg += dialogue.constructPlyrStatMessage(
                        user_info)
                    response_msg += "```"

        else:
            response_msg = dialogue.retrieveDialogue("unknown")

        await message.channel.send(response_msg)

    if message.content.startswith("Hi"):
        await message.channel.send('hey!')


def get_traceback(e):
    lines = traceback.format_exception(type(e), e, e.__traceback__)
    return ''.join(lines)


client.run(os.getenv('TOKEN'))
