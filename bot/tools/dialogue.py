from queue import Empty
from re import L
from secrets import randbelow
from tabnanny import check
from table2ascii import table2ascii


class Dialogue:
    def __init__(self, inside_jokes):
        self.reset(inside_jokes)

    def reset(self, inside_jokes):

        self.threshold = 3  # How long to "freeze" answers for

        self.dialogue_dict = {
            "already_joined": ["You've already joined the game homie!"],
            "already_won_guess":
            ["Youve already completed this game. Stop showing off"],
            "aready_won_join": [
                "Mr money bags over here wants to join twice?? :money_with_wings:"
            ],
            "already_won_start":
            ["You already won, give the others a chance ya knob!"],
            "correct_guess": [],
            "!game_exists": [
                "You need to start a game first dumbass",
                "Game has not yet started!"
            ],
            "dupe_guess": [
                "The rules of of Wordle are so simple and, yet, you still don't understand you can't guess the same word twice...",
                "Guessing the same word twice? Bold strategy. Let's see how that plays out."
            ],
            "guessing": ["Guessing!"],
            "incorrect_len":
            ["Your guess does not match the games word length: "],
            "invalid_word": [
                "I...thought this went without saying but...guesses need to be legitimate words."
            ],
            "joining_game": ["Joined the current game."],
            "limit_reached": ["Youve reached your limit! Cuck!"],
            "list_plyrs": [],
            "server_err": ["OOPS!"],
            "spoiler_missing": [
                "OOPS! Spoiler mode is ON and your word wasn't tagged as a spoiler :face_with_hand_over_mouth:"
            ],
            "starting_game": ["Started the game!"],
            "submit_guess": [],
            "unknown": ["Unknown command, ya dunce!!"],
            "wrong_guess": []
        }

        self.recent_dialogue_dict = {
            "already_joined": [],
            "already_won_guess": [],
            "already_won_join": [],
            "already_won_start": [],
            "correct_guess": [],
            "dupe_guess": [],
            "!game_exists": [],
            "guessing": [],
            "incorrect_len": [],
            "invalid_word": [],
            "joining_game": [],
            "limit_reached": [],
            "list_plyrs": [],
            "starting_game": [],
            "spoiler_missing": [],
            "submit_guess": [],
            "wrong_guess": [],
            "unknown": [],
            "!game_exists": [],
        }

        self.green_square = ":green_square:"
        # self.black_square = ":blue_square:"
        self.black_square = ":black_large_square:"
        self.yellow_square = ":yellow_square:"
        self.arrow_forward = ":arrow_forward:"
        self.turtle = ":turtle:"
        self.banned_words = ["Jordan", "Thomas"]

        self.inside_jokes = inside_jokes  #Include name related jokes and lines or not

        self.collectDialogue()

    #Store all available dialoge lines on init (less file access) one 'n done
    #
    def collectDialogue(self):
        types = self.dialogue_dict.keys()
        try:
            for category in types:
                with open(r"./bot/tools/dialogue_lines/" + category + ".txt",
                          "r") as txt:
                    for line in txt:
                        self.dialogue_dict[category].append(line)
        except Exception as e:
            print("Error opening files for dialogue...")
            print(e)

    #Gimme a dialogue line
    def retrieveDialogue(self, style):

        if style not in self.dialogue_dict.keys():
            return False

        interesting_dict = self.dialogue_dict[style]

        list_len = len(interesting_dict)

        if (list_len <= 1):  #Only one choice
            return interesting_dict[0]
        choice = 0

        if not (list_len >=
                self.threshold * 2):  #Not enough to enforce randomization
            return interesting_dict[choice]
        else:  #Have some fun :)
            while (choice == 0):
                choice = randbelow(list_len - 1)
                if (choice not in self.recent_dialogue_dict[style]
                        and self.ijMode(interesting_dict[choice])):
                    self.handleNewChoice(choice, style)
                else:
                    choice = 0

            return interesting_dict[choice]

    #Ensures we dont get the same dialogue too often
    def handleNewChoice(self, choice, style):
        recent_dict = self.recent_dialogue_dict[style]

        if (len(recent_dict) < self.threshold):
            recent_dict.append(choice)
        else:
            recent_dict.pop(0)
            recent_dict.append(choice)

    def helpMenu(self):
        help = "Wordle Turtle "+self.turtle+" Help Menu v1.0: \n"\
        +self.arrow_forward + "To start a new game type either `!start game [#] letters` OR `!sg[#]l` (Between 4-9 letters ONLY) \n"\
        +self.arrow_forward + "Guess -> !guess ||word|| (Ensure your guess is tagged as a spoiler using `||`!) \n"\
        +self.arrow_forward + "List the current players -> !lp/!players/!whos  playing? \n"\
        +self.arrow_forward + "Help -> !help (shows this menu)"
        return help

    def ijMode(self, choice):
        if self.inside_jokes:
            return True
        else:
            for word in self.banned_words:
                if word in choice:
                    return False

        return True

    #FIXME: "PLAYERS" should be emojis, but different emojis rendered on different platforms
    #AND this function cannot print emojis yet
    def constructCurrentPlyrsTbl(self, user_info):
        headers = ["Name", "Guesses", "Correct"]
        body = []

        check_symbol = "✓"
        x_symbol = "x"

        for info in user_info:
            print(info)
            tmp = []
            tmp.append(info[0])
            tmp.append(str(info[1]) + "/5")
            tmp.append(check_symbol) if info[2] else tmp.append(x_symbol)
            body.append(tmp)

        return table2ascii(header=headers, body=body)

    def constructGuessMessage(self, user_info):

        letters = [
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
        ]
        message = "\n\n"
        message += "Wordle 666 :turtle: \n"

        guesses = user_info["guesses"]
        current_word = user_info["target_word"]
        word_len = user_info["target_len"]

        for guess in guesses:
            guess_arr = list(guess)
            word_arr = list(current_word)
            match_count = 0
            for i in range(0, len(guess_arr)):

                ltr_upper = guess_arr[i]
                ltr_upper = ltr_upper.upper()

                if ltr_upper in letters:
                    letter = "**~~"
                    letter += letters[letters.index(ltr_upper)]
                    letter += "~~**"
                    letters[letters.index(ltr_upper)] = str(letter)

                if guess_arr[i] == word_arr[i]:
                    match_count += 1
                    message += self.green_square
                elif guess_arr[i] in word_arr:
                    message += self.yellow_square
                else:
                    message += self.black_square
            message += " ====> ||~~" + guess + "~~||"
            message += "\n"

        message += "\n"

        if (match_count is word_len):
            message += "Congrats! You won! :tada: :partying_face: :weary:"
            message += "\n\n"

        else:
            message += "||"
            for letter in letters:
                message += letter + " "
            message += "||"
            message += "\n\n"

        return message

    def constructPlyrStatMessage(self, stats):
        headers = ["Name", "Wins", "Losses", "Win %"]

        print(stats)

        win_percentage = round((stats[5] / stats[3]) * 100)
        body = [[stats[1], stats[5], stats[6], str(win_percentage) + "%"]]

        return table2ascii(header=headers, body=body)

    def constructAllPlyrStatMessage(self, stats):
        print(stats)

        headers = ["Name", "Wins", "Losses", "Win %"]
        body = []
        for stat in stats:
            win_percentage = round((stat[5] / stat[3]) * 100)
            body.append([stat[1], stat[5], stat[6], str(win_percentage) + "%"])

        return table2ascii(header=headers, body=body)