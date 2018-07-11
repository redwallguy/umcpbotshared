import discord
import asyncio
import os
from discord.ext import commands
import redis
import psycopg2

bot = commands.Bot(command_prefix="!")
token = os.environ.get("discToken")
r = redis.from_url(os.environ.get("REDIS_URL"))

dburl = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(dburl, sslmode="require")
cur = conn.cursor()


class Games:
    def __init__(self):
        cur.execute("SELECT * FROM games;")
        glist = cur.fetchall()
        self.games = {}
        for g in glist:
            self.games[g[0]] = []
        for key in self.games:
            cur.execute("SELECT (alias) FROM aliases WHERE game = %s", key)
            alilist = cur.fetchall()
            for ali in alilist:
                self.games[key].append(ali[0])

    def get_games(self):
        return self.games

    def add_game(self, game):
        try:
            cur.execute("INSERT INTO (games) VALUES (%s)", game)
            self.games[game] = []
        except:
            return "Game already exists."

    def add_alias(self, alias, game):
        try:
            cur.execute("INSERT INTO aliases (alias, game) VALUES (%s,%s)", alias, game)
            self.games[game].append(alias)
        except:
            return "Oops! Something went wrong."

    def remove_alias(self, alias, game):
        try:
            cur.execute("DELETE FROM aliases WHERE alias = %s", alias)
            self.games[game].remove(alias)
        except:
            return






