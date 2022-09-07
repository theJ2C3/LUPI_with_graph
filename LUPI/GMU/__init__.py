from ast import Num
from email.policy import default
from nntplib import GroupInfo
from otree.api import *

from io import BytesIO
from base64 import b64encode
import urllib
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np


doc = """
this is an app to ask players guess the lowest unique positive int
"""


class C(BaseConstants):
    NAME_IN_URL = 'GMU'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2
    INSTRUCTIONS_TEMPLATE = 'GMU/instructions.html'
    GUESS_MIN = 1
    GUESS_MAX = 100
    PAYOFF = cu(10)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # pass
    winnernum = models.IntegerField()
    winnername = models.StringField()


class Player(BasePlayer):
    playerName= models.StringField(
        label = "Player Name/玩家名稱或暱稱"
        # default = 1
        )
    NumInput = models.IntegerField(
        label="Please pick a number from 1 to 100",
        min=C.GUESS_MIN,
        max= C.GUESS_MAX,
        # default = 1
        )
    isWinner = models.BooleanField(default = False)



# FUNCTIONS

# def sorted_list(group: Group):
#     guess_players_dict = {}  # {NumInput: players}

#     # save all data as dic
#     for p in group.get_players():
#         if p.NumInput in guess_players_dict:
#             players = guess_players_dict[p.NumInput]
#         else:
#             players = []
#         players.append(p)
#         guess_players_dict[p.NumInput] = players  

#     # ASGPD = sorted(guess_players_dict.items())
#     return sorted(guess_players_dict.items())




def create_figure(player:Player):

    guess_players_dict = {}  # {NumInput: players}

    # save all data as dic
    for p in player.group.get_players():
        if p.NumInput in guess_players_dict:
            players = guess_players_dict[p.NumInput]
        else:
            players = []
        players.append(p)
        guess_players_dict[p.NumInput] = players
    
    sorted_guess_count = sorted(guess_players_dict.items())
    # sorted_guess_count = sorted_list()
    guess_distrubution = [0 for i in range(C.GUESS_MAX)]

    for num, players in sorted_guess_count:
        guess_distrubution[num] = len(players)

    ydata = guess_distrubution
    # ydata = sorted_list(group)
    xdata = [i+1 for i in range(C.GUESS_MAX)]
    xlabel = [ None for i in range(C.GUESS_MAX)]
    ylabel = [i  for i in range(max(guess_distrubution)+1)]
    for i in range(C.GUESS_MAX):
        if i% 5 == 0:
            xlabel[i] = i

    # plt.clf()
    
    plt.figure(figsize=(7, 3))
    # plt.plot(xdata, ydata, color='red', marker='d', markersize=10)
    # plt.bar(*np.unique(ydata, return_counts=True))
    plt.bar(xdata, ydata)
    
    # plt.plot(range(10), np.random.rand(10), color='red', marker='d', markersize=10)

    fig = plt.gcf()
    plt.xlabel("Guessed Number")
    plt.ylabel("Guessed Number Count")
    plt.title("Distribution of Guesses")
    plt.yticks(ylabel)
    plt.xticks(xdata,xlabel)

    buf = BytesIO()        
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    string = b64encode(buf.read())

    return urllib.parse.quote(string)


def set_payoff(group: Group):
    guess_players_dict = {}  # {NumInput: players}

    # save all data as dic
    for p in group.get_players():
        if p.NumInput in guess_players_dict:
            players = guess_players_dict[p.NumInput]
        else:
            players = []
        players.append(p)
        guess_players_dict[p.NumInput] = players

    if Player.round_number != 1 :
        for p in group.get_players():
            p.playerName = p.in_round(1).playerName    

    # sorted_guess_count = sorted_list()

    winner = None

    # find the winner
    for num, players in sorted(guess_players_dict.items()):
    # for num, players in sorted(sorted_guess_count):
        if (winner is None) and (len(players) == 1):
            winner = players[0]
            winner.isWinner = True
            winner.payoff = C.PAYOFF
            group.winnernum = num
            group.winnername = str(winner.playerName)
    
    if winner == None:
        group.winnernum = 100
        # group.winnername = "no one" 


# PAGES

class Introduction(Page):
    def is_displayed(player: Player):
        return player.round_number == 1
    timeout_seconds = 100


class IdPage(Page):
    form_model = 'player'
    form_fields = ['playerName']
    def is_displayed(player: Player):
        return player.round_number == 1


class Guess(Page):
    form_model = 'player'
    # names must correspond to fields in models.py
    form_fields = ['NumInput']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoff'
    # pass

class Results(Page):
    # https://pietrobattiston.it/otree_mytips

    def vars_for_template(player: Player):
        return {'my_img' : create_figure(player)}

    # <img width="100%" src="data:image/png;base64,{{ my_img }}">
    # pass

class Final(Page):
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    # <img width="100%" src="data:image/png;base64,{{ my_img }}">
    # pass

page_sequence = [Introduction, IdPage, Guess, ResultsWaitPage, Results, Final]
