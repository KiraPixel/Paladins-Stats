import os

from flask import Flask, render_template, redirect, url_for, request
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache


import ps
import characters_cash
from config import settings

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)
cache = Cache(config={'CACHE_TYPE': 'simple'})

app.secret_key = b"asdasdasd asda sd asd"
app.debug = True
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "false"

app.config["DISCORD_CLIENT_ID"] = settings['DISCORD_CLIENT_ID']
app.config["DISCORD_CLIENT_SECRET"] = settings['DISCORD_CLIENT_SECRET']
app.config["DISCORD_REDIRECT_URI"] = f"http://{settings['host']}{settings['DISCORD_REDIRECT_URI']}"
discord = DiscordOAuth2Session(app)

user_authorized = False

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return discord.create_session(scope=['identify'])


@app.route('/logout')
def logout():
    discord.revoke()
    return redirect('/')


@app.route('/profile')
def profile():
    return redirect('/')


@app.route('/callback')
def callback():
    discord.callback()
    return redirect('/')


@app.route('/characters')
def characters():
    champions = characters_cash.PaladinsDatabase('paladins.db')
    champions = champions.get_cashed_champions()
    support = [char for char in champions if char[3] == 'Support']
    tank = [char for char in champions if char[3] == 'Line']
    flank = [char for char in champions if char[3] == 'Flanker']
    damage = [char for char in champions if char[3] == 'Damage']
    return render_template('characters.html', support=support, tank=tank, flank=flank, damage=damage)


@app.route('/guides')
def guides():
    return redirect('/characters')


@app.route('/players/')
def players():
    return redirect('/players/search')

@app.route('/players/search', methods=['GET', 'POST'])
@limiter.limit("150 per minute")
def search_players():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        players = ps.SearchPlayer(search_query)
        return render_template('search_results.html', players=players)
    return render_template('search_form.html')


@app.route('/players/<int:player_id>')
def player_profile(player_id):
    player_info = ps.Player(player_id)
    player_match = ps.GetPlayersMatchs(player_id)
    return render_template('profile.html', ps=player_info, pc=player_match)


@app.route('/match')
def match():
    match_id = request.args.get('match')
    characters_cashed = characters_cash.PaladinsDatabase('paladins.db')
    if match_id:
        player_info = ps.GetMatchInfo(match_id)
        players_info = []
        for player in player_info:
            characters = characters_cashed.get_lite_champion(player.ChampionId),
            player_dict = {
                "Character_avatar": characters[0][1],
                "Character_name": characters[0][0],
                "playerName": player.playerName,
                "playerID": player.playerId,
                "Account_Level": player.Account_Level,
                "Gold_Earned": player.Gold_Earned,
                "Kills_Player": player.Kills_Player,
                "Deaths": player.Deaths,
                "Assists": player.Assists,
                "Objective_Assists": player.Objective_Assists,
                "Damage_Player": player.Damage_Player,
                "Damage_Mitigated": player.Damage_Mitigated,
                "Healing": player.Healing
            }

            players_info.append(player_dict)
        return render_template('matchinfo.html', players_info=players_info)
    else:
        return render_template('matchsearcher.html')


@app.context_processor
def inject_user_authorized():
    if discord.authorized:
        user = discord.fetch_user()
    else:
        user = None
    return dict(user=user, user_authorized=discord.authorized)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    limiter.init_app(app)
    app.run(host=settings['host'])