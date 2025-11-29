class CombinedUserData:
    def __init__(
        self,
        spotify=None,
        valorant=None,
        anime=None,
        steam=None,
        inputs=None,
    ):
        self.spotify = spotify or {}
        self.valorant = valorant or {}
        self.anime = anime or {}
        self.steam = steam or {}
        self.inputs = inputs or {}

    def as_dict(self):
        return {
            "spotify": self.spotify,
            "valorant": self.valorant,
            "anime": self.anime,
            "steam": self.steam,
            "inputs": self.inputs,
            "sources": [
                *( ["Spotify"] if self.spotify else []),
                *( ["Valorant"] if self.valorant else []),
                *( ["AniList"] if self.anime else []),
                *( ["Steam"] if self.steam else []),
            ],
        }

    def prompt_block(self):
        parts = []
        if self.spotify:
            parts.append(
                f"Spotify Data:\nTop Artists: {self.spotify.get('top_artists')}\nRecent Tracks: {self.spotify.get('recent_tracks')}"
            )
        if self.valorant:
            parts.append(
                "Valorant Data:\n"
                f"IGN: {self.valorant.get('ign')}\nRank: {self.valorant.get('rank')} (ELO {self.valorant.get('elo')})\n"
                f"K/D Ratio: {self.valorant.get('k_d_ratio')}\nHeadshot Rate: {self.valorant.get('headshot_rate')}%\n"
                f"Main Agent: {self.valorant.get('main_agent')}\nRecent Matches: {self.valorant.get('recent_matches')}"
            )
        if self.anime:
            parts.append(
                "AniList Data:\n"
                f"Username: {self.anime.get('username')}\nDays Wasted Watching: {self.anime.get('days_wasted')}\n"
                f"Total Episodes Watched: {self.anime.get('total_episodes')}\n"
                f"Anime Watching Count: {self.anime.get('anime_watching')}\nAnime Completed Count: {self.anime.get('anime_completed')}\n"
                f"Currently Watching: {self.anime.get('anime_watching_list')}\n"
                f"Completed Anime (Top 10): {self.anime.get('anime_completed_list')}\n"
                f"Top Anime Genres: {self.anime.get('top_anime_genres')}\nFavorite Anime: {self.anime.get('favorite_anime')}\n"
                f"Chapters Read: {self.anime.get('chapters_read')}\nVolumes Read: {self.anime.get('volumes_read')}\n"
                f"Manga Reading Count: {self.anime.get('manga_reading')}\nManga Completed Count: {self.anime.get('manga_completed')}\n"
                f"Currently Reading Manga: {self.anime.get('manga_reading_list')}\n"
                f"Completed Manga (Top 10): {self.anime.get('manga_completed_list')}\n"
                f"Top Manga Genres: {self.anime.get('top_manga_genres')}\nFavorite Manga: {self.anime.get('favorite_manga')}"
            )
        if self.steam:
            parts.append(
                "Steam Data:\n"
                f"Player: {self.steam.get('player_name')} (SteamID: {self.steam.get('steam_id')})\n"
                f"Profile: {self.steam.get('profile_url')}\n"
                f"Total Playtime: {self.steam.get('total_playtime_hours')}h\n"
                f"Top Games: {self.steam.get('top_games')}\n"
                f"Recent Games: {self.steam.get('recent_games')}"
            )
        input_summary = self._format_input_summary()
        if input_summary:
            parts.append("User Provided Identifiers:\n" + input_summary)

        if not parts:
            return "No telemetry received. Invent a roast anyway."

        return "\n\n".join(parts)

    def _format_input_summary(self):
        if not self.inputs:
            return ""

        lines = []
        spotify_name = self.inputs.get("spotify_name")
        if spotify_name:
            lines.append(f"- Spotify account connected as {spotify_name}.")

        valorant_name = self.inputs.get("valorant_name")
        valorant_tag = self.inputs.get("valorant_tag")
        if valorant_name and valorant_tag:
            region = (self.inputs.get("valorant_region") or "NA").upper()
            lines.append(
                f"- Valorant IGN {valorant_name}#{valorant_tag} ({region}) provided even if stats are missing."
            )

        anilist_user = self.inputs.get("anilist_user")
        if anilist_user:
            lines.append(f"- AniList profile submitted: {anilist_user}.")

        steam_id = self.inputs.get("steam_id") or self.inputs.get("steam_vanity")
        if steam_id:
            lines.append(f"- Steam identifier: {steam_id}.")

        if not lines:
            return ""

        return "\n".join(lines)
