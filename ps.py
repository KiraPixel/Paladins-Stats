from pyrez.api import PaladinsAPI

from config import hirez_api
import threading

# Укажите ваш API-ключ, который вы получили после регистрации на сайте разработчиков игры
DEV_ID = hirez_api['DEV_ID']
AUTH_KEY = hirez_api['AUTH_KEY']
DEFAULT_AVATAR_URL = "https://media.discordapp.net/attachments/1098027082031828992/1098324800331587594/AKedOLRn5an-FXRAMJjqOv_gPRvWBlDmDZ-NymbH_zCFs900-c-k-c0x00ffffff-no-rj.png?width=651&height=651"
MAX_SEARCH = 12

# Определите количество потоков, которые вы хотите использовать
NUM_THREADS = 4

# Создаем объект API и выполняем запрос к API-интерфейсу для получения информации об аккаунте
api = PaladinsAPI(devId=DEV_ID, authKey=AUTH_KEY)


class Player:
    def __init__(self, value):
        self.player_object = api.getPlayer(value)
        self.player_status_object = api.getPlayerStatus(value)
        self.player_ingame_status = self.player_status_object.status_string
        self.player_nick_name = self.player_object.hz_player_name
        self.player_id = self.player_object.ActivePlayerID
        self.player_platform = self.player_object.Platform
        self.player_title = self.player_object.Title
        self.player_avatar = self.player_object.AvatarURL if self.player_object.AvatarURL else DEFAULT_AVATAR_URL
        self.region = self.player_object.Region
        self.in_game_hours = self.player_object.HoursPlayed
        self.created_date = self.player_object.Created_Datetime
        self.last_login = self.player_object.Last_Login_Datetime
        self.level = self.player_object.Level
        self.total_wins = self.player_object.Wins
        self.total_losses = self.player_object.Losses
        self.ranked_rank = self.player_object.RankedKBM['Tier']
        self.ranked_points = self.player_object.RankedKBM['Points']


def GetChampions():
    return api.getChampions()


import pyrez.exceptions

def GetPlayersMatchs(playerId):
    try:
        return api.getMatchHistory(playerId)
    except pyrez.exceptions.MatchException as e:
        pass


def GetMatchInfo(matchId):
    return api.getMatch(matchId)


def SearchPlayer(value):
    search_result = api.searchPlayers(value)
    search_table = []
    if search_result:
        threads = []
        result_list = []
        for i, player in enumerate(search_result):
            player_id = player.playerId
            thread = threading.Thread(target=get_player_info, args=(player_id, result_list))
            threads.append(thread)
            thread.start()
            if i == 99 or MAX_SEARCH == len(result_list):
                break
        for thread in threads:
            thread.join()
        search_table = result_list
    return search_table


def get_player_info(player_id, result_list):
    api_player = api.getPlayer(player_id)
    player_avatar = api_player.AvatarURL or DEFAULT_AVATAR_URL
    if api_player.hz_player_name:
        player_dist = {
            "avatar": player_avatar,
            "nickname": api_player.hz_player_name,
            "level": api_player.Level,
            "player_id": player_id
        }
        result_list.append(player_dist)


def search_players_multithreaded(values):
    result = []
    threads = []
    for value in values:
        thread = threading.Thread(target=lambda: result.append(SearchPlayer(value)))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    return result