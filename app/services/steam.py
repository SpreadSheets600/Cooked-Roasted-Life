import os
import requests


class SteamService:
    def __init__(self):
        self.api_key = os.getenv("STEAM_API_KEY")

    def is_ready(self):
        return bool(self.api_key)

    def _resolve_vanity(self, vanity):
        try:
            resp = requests.get(
                "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/",
                params={"key": self.api_key, "vanityurl": vanity},
                timeout=8,
            )
            data = resp.json().get("response", {})
            if data.get("success") == 1:
                return data.get("steamid")
        except Exception:
            pass
        return None

    def get_roast_data(self, steam_id=None, vanity=None):
        if not self.is_ready():
            return {}

        if not steam_id and vanity:
            steam_id = self._resolve_vanity(vanity)

        if not steam_id:
            return {}

        # Get player summary (name, profile, etc.)
        player_name = None
        profile_url = None
        try:
            summary_resp = requests.get(
                "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/",
                params={"key": self.api_key, "steamids": steam_id},
                timeout=8,
            )
            summary_data = summary_resp.json().get("response", {})
            players = summary_data.get("players", [])
            if players:
                player = players[0]
                player_name = player.get("personaname")
                profile_url = player.get("profileurl")
        except Exception:
            pass

        # Owned games
        try:
            owned_resp = requests.get(
                "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/",
                params={
                    "key": self.api_key,
                    "steamid": steam_id,
                    "include_appinfo": 1,
                    "include_played_free_games": 1,
                    "format": "json",
                },
                timeout=10,
            )
            owned = owned_resp.json().get("response", {})
        except Exception:
            owned = {}

        games = owned.get("games", [])
        total_hours = (
            round(sum(g.get("playtime_forever", 0) for g in games) / 60, 1)
            if games
            else 0
        )
        top_games = sorted(
            games, key=lambda g: g.get("playtime_forever", 0), reverse=True
        )[:10]
        top_games_fmt = [
            f"{g.get('name')} ({round(g.get('playtime_forever', 0) / 60, 1)}h)"
            for g in top_games
        ]

        # Recent games
        try:
            recent_resp = requests.get(
                "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/",
                params={"key": self.api_key, "steamid": steam_id, "format": "json"},
                timeout=8,
            )
            recent = recent_resp.json().get("response", {})
        except Exception:
            recent = {}

        recent_fmt = [
            f"{g.get('name')} ({round(g.get('playtime_2weeks', 0) / 60, 1)}h last 2w)"
            for g in recent.get("games", [])[:10]
        ]

        return {
            "steam_id": steam_id,
            "player_name": player_name,
            "profile_url": profile_url,
            "total_playtime_hours": total_hours,
            "top_games": top_games_fmt,
            "recent_games": recent_fmt,
            "type": "steam",
        }
