import re


def msgMatcher(match_type, msg):

    regex_dict = {
        "START_GAME_REGEX": [r"start game [5-9] letters", r"sg[1-9]l?"],
        "JOIN_GAME_REGEX": [r"join game", r"i want in", r"join"],
        "PLYR_GUESS_REGEX":
        [r"guess [A-Za-z]*", r"my guess is [A-Za-z]*", r"is it [A-Za-z]*"],
        "RUN_CHECK_REGEX": [r"(is the |is)*game running"],
        "PLYR_CHECK_REGEX":
        [r"whos playing", r"player list", r"^players$", r"^lp$"],
        "HELP_REGEX": [r"help"],
        "STATS_REGEX": [r"stats", r"stat me", r"leaderboard"]
    }

    if (match_type == "START_GAME_REGEX"):
        interesting_list = regex_dict[match_type]

    elif (match_type == "JOIN_GAME_REGEX"):
        interesting_list = regex_dict[match_type]

    elif (match_type == "PLYR_GUESS_REGEX"):
        interesting_list = regex_dict[match_type]

    elif (match_type == "RUN_CHECK_REGEX"):
        interesting_list = regex_dict[match_type]

    elif (match_type == "PLYR_CHECK_REGEX"):
        interesting_list = regex_dict[match_type]

    elif (match_type == "HELP_REGEX"):
        interesting_list = regex_dict[match_type]

    elif (match_type == "STATS_REGEX"):
        interesting_list = regex_dict[match_type]

    else:
        return False

    for exp in interesting_list:
        if re.search(exp, msg): return True

    return False


#Used to check for "valid" words (to discourage guessing gibberish)
#store in a set O(1) - bad memory good lookup time
def initDictionary():
    with open(r"./bot/tools/words/valid_words.txt") as word_file:
        valid_words = set(word_file.read().split())
    return valid_words
