import io
import os
import logging
import json
import zipfile
from flask import abort, Blueprint, Response, render_template, redirect, send_file, send_from_directory, session
from zenora import APIClient

from ..core import core
from ..data import load_data
from ..config import BASEDIR
from ..modules.checker import is_game_admin, is_admin


log = logging.getLogger(__name__)
main = Blueprint("main", __name__)


@main.after_request
def checking(response: Response):
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "deny"
    return response
    

@main.route("/")
def index():
    if "token" in session:
        bearer_client = APIClient(session.get("token"), bearer=True)
        current_user = bearer_client.users.get_current_user()
        team, _ = core.check_player(current_user.username)
        if team is None and is_game_admin():
            team = "Game Admins"
        teams = [team for team in core.teams.values() if team.name != "admins"]
        return render_template("index.html", current_user=current_user.username, team=team, graph=core.metro.graph, avater_url=current_user.avatar_url, teams=teams)
    
    return redirect("/login")


@main.route("/admin")
def admin():
    if "token" in session:
        bearer_client = APIClient(session.get("token"), bearer=True)
        current_user = bearer_client.users.get_current_user()
        team, is_admin = core.check_player(current_user.username)

        if team is None and is_game_admin():
            team = "Game Admins"
    
        if is_admin:
            return render_template("admin.html", current_user=current_user.username, team=team)
        
    return redirect("/")


@main.route("/download_graph")
def download_graph():
    with io.StringIO() as file:
        json.dump(core.metro.graph, file, ensure_ascii=False, indent=4)
        response = send_file(file.name, as_attachment=True, download_name="graph.json")
        
    return response


@main.route("/combo")
def combo():
    if "token" in session:
        bearer_client = APIClient(session.get("token"), bearer=True)
        current_user = bearer_client.users.get_current_user()
        team, _ = core.check_player(current_user.username)

        if team is None and is_game_admin():
            team = "Game Admins"

        return render_template("combo.html", current_user=current_user.username, team=team, graph=core.metro.graph, combos=load_data("combo"), avater_url=current_user.avatar_url)
    
    return redirect("/")


@main.route("/team_admin")
def team_admin():
    if "token" in session:
        bearer_client = APIClient(session.get("token"), bearer=True)
        current_user = bearer_client.users.get_current_user()
        team, _ = core.check_player(current_user.username)
        
        if team is None and is_game_admin():
            team = "Game Admins"

        if is_admin():
            return render_template("team_admin.html", current_user=current_user.username, team=team, graph=core.metro.graph, avater_url=current_user.avatar_url)
        
    return redirect("/")


@main.route("/card")
def card():
    if "token" in session:
        bearer_client = APIClient(session.get("token"), bearer=True)
        current_user = bearer_client.users.get_current_user()
        team, _ = core.check_player(current_user.username)

        if team is None and is_game_admin():
            team = "Game Admins"
        
        if is_admin():
            return render_template("card.html", current_user=current_user.username, team=team, graph=core.metro.graph)
        
    return redirect("/")


@main.route("/dice")
def dice():
    if "token" in session:
        bearer_client = APIClient(session.get("token"), bearer=True)
        current_user = bearer_client.users.get_current_user()
        team, _ = core.check_player(current_user.username)

        if team is None and is_game_admin():
            team = "Game Admins"
        
        if is_admin():
            return render_template("dice.html", current_user=current_user.username, team=team, graph=core.metro.graph)

    return redirect("/")


@main.route("/initialization")
def initialization():
    if "token" in session:
        bearer_client = APIClient(session.get("token"), bearer=True)
        current_user = bearer_client.users.get_current_user()
        team, _ = core.check_player(current_user.username)

        if team is None and is_game_admin():
            team = "Game Admins"
        
        if is_admin():
            return render_template("initialization.html", current_user=current_user.username, team=team, graph=core.metro.graph)

    return redirect("/")


@main.route("/log")
def server_log():
    log_directory = os.path.join(BASEDIR, "logs")
    # log_filename = "app.log"
    
    if not is_game_admin():
        abort(404)

    bearer_client = APIClient(session.get("token"), bearer=True)
    current_user = bearer_client.users.get_current_user()
    
    log.info(f"{current_user.username}({current_user.id}) is checking the log file")
    
    with zipfile.ZipFile(log_directory + ".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(log_directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(log_directory))
                zipf.write(file_path, arcname)

    return send_file(log_directory + ".zip", as_attachment=True, download_name="logs.zip")
    # return send_from_directory(log_directory, log_filename)