import os
import requests
from collections import Counter


class ValorantService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("HENRIK_API_KEY")
        self.base_url = "https://api.henrikdev.xyz/valorant"
        self.headers = {"Authorization": f"{self.api_key}"} if self.api_key else {}

    def get_roast_data(self, name, tag, region="na"):
        mmr_url = f"{self.base_url}/v3/mmr/{region}/pc/{name}/{tag}"
        mmr_res = requests.get(mmr_url, headers=self.headers)
        rank = "Unranked"
        elo = 0

        if mmr_res.status_code == 200:
            data = mmr_res.json()

            if data.get("data") and data["data"].get("current"):
                rank = data["data"]["current"]["tier"]["name"]
                elo = data["data"]["current"]["elo"]
        else:
            return {}

        matches_url = f"{self.base_url}/v4/matches/{region}/pc/{name}/{tag}"
        matches_res = requests.get(matches_url, headers=self.headers)

        if matches_res.status_code != 200:
            return {
                "type": "valorant",
                "ign": f"{name}#{tag}",
                "rank": rank,
                "elo": elo,
            }

        matches = matches_res.json().get("data", [])[:5]
        total_kills = total_deaths = total_headshots = total_shots = 0
        kd_list = []
        agents = []
        wins = 0

        for match in matches:
            me = next(
                (
                    p
                    for p in match.get("players", [])
                    if p["name"].lower() == name.lower()
                    and p["tag"].lower() == tag.lower()
                ),
                None,
            )

            if not me:
                continue

            k = me["stats"]["kills"]
            d = me["stats"]["deaths"]
            h = me["stats"]["headshots"]

            total_kills += k
            total_deaths += d
            total_headshots += h
            total_shots += h + me["stats"]["bodyshots"] + me["stats"]["legshots"]

            agents.append(me["agent"]["name"])
            kd_list.append(k / d if d else k)
            my_team = me["team_id"].lower()

            win_team = next(
                (t["team_id"] for t in match.get("teams", []) if t.get("won")), None
            )

            if win_team and win_team.lower() == my_team:
                wins += 1

        avg_kd = round(total_kills / total_deaths, 2) if total_deaths else total_kills
        headshot_rate = (
            round((total_headshots / total_shots) * 100, 2) if total_shots else 0
        )

        main_agent = Counter(agents).most_common(1)[0][0] if agents else "Unknown"
        recent_perf = f"{wins}W/{len(matches) - wins}L last {len(matches)}"

        return {
            "type": "valorant",
            "ign": f"{name}#{tag}",
            "rank": rank,
            "elo": elo,
            "k_d_ratio": avg_kd,
            "main_agent": main_agent,
            "recent_matches": recent_perf,
            "headshot_rate": headshot_rate,
        }
