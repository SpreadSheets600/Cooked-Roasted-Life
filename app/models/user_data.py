class CombinedUserData:
    def __init__(self, spotify=None, valorant=None, anime=None):
        self.spotify = spotify or {}
        self.valorant = valorant or {}
        self.anime = anime or {}

    def as_dict(self):
        return {
            "spotify": self.spotify,
            "valorant": self.valorant,
            "anime": self.anime,
            "sources": [
                *(["Spotify"] if self.spotify else []),
                *(["Valorant"] if self.valorant else []),
                *(["AniList"] if self.anime else []),
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
        return "\n\n".join(parts)
