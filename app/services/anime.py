import requests


class AnimeService:
    def __init__(self):
        self.url = "https://graphql.anilist.co"

    def get_roast_data(self, username):
        query = """
        query ($name: String) {
          User(name: $name) {
            name
            siteUrl
            statistics { 
              anime { 
                count 
                minutesWatched 
                episodesWatched 
                statuses { status count } 
                genres(limit:5, sort: COUNT_DESC){ genre count } 
              } 
              manga { 
                count 
                chaptersRead 
                volumesRead 
                statuses { status count } 
                genres(limit:5, sort: COUNT_DESC){ genre count } 
              } 
            }
            favourites { 
              anime(perPage: 10){ nodes { title { romaji english } } } 
              manga(perPage:10){ nodes { title { romaji english } } } 
            }
          }
          animeWatching: MediaListCollection(userName: $name, type: ANIME, status: CURRENT) {
            lists {
              entries {
                media {
                  title { romaji english }
                }
              }
            }
          }
          animeCompleted: MediaListCollection(userName: $name, type: ANIME, status: COMPLETED, sort: SCORE_DESC) {
            lists {
              entries {
                media {
                  title { romaji english }
                }
              }
            }
          }
          mangaReading: MediaListCollection(userName: $name, type: MANGA, status: CURRENT) {
            lists {
              entries {
                media {
                  title { romaji english }
                }
              }
            }
          }
          mangaCompleted: MediaListCollection(userName: $name, type: MANGA, status: COMPLETED, sort: SCORE_DESC) {
            lists {
              entries {
                media {
                  title { romaji english }
                }
              }
            }
          }
        }
        """
        variables = {"name": username}

        try:
            response = requests.post(
                self.url, json={"query": query, "variables": variables}, timeout=10
            )

            if response.status_code != 200:
                return {}

            data = response.json()

            if "errors" in data:
                return {}

            user = data["data"]["User"]
            animestats = user["statistics"]["anime"]
            mangastats = user["statistics"]["manga"]

            minutes = animestats["minutesWatched"]
            days_wasted = round(minutes / 60 / 24, 1)

            def status_count(block, key):
                for s in block.get("statuses", []):
                    if s["status"] == key:
                        return s["count"]
                return 0

            anime_watching = status_count(animestats, "CURRENT")
            anime_completed = status_count(animestats, "COMPLETED")
            manga_reading = status_count(mangastats, "CURRENT")
            manga_completed = status_count(mangastats, "COMPLETED")

            def extract_titles(nodes, limit=10):
                titles = []

                for node in nodes[:limit]:
                    t = node["title"]["english"] or node["title"]["romaji"]
                    titles.append(t)

                return titles

            def extract_from_lists(list_data, limit=10):
                titles = []

                for lst in list_data.get("lists", []):
                    for entry in lst.get("entries", []):
                        if len(titles) >= limit:
                            break

                        media = entry.get("media", {})
                        title = media.get("title", {})
                        t = title.get("english") or title.get("romaji")

                        if t:
                            titles.append(t)

                    if len(titles) >= limit:
                        break
                return titles[:limit]

            anime_watching_list = extract_from_lists(
                data["data"].get("animeWatching", {}), 10
            )
            anime_completed_list = extract_from_lists(
                data["data"].get("animeCompleted", {}), 10
            )
            manga_reading_list = extract_from_lists(
                data["data"].get("mangaReading", {}), 10
            )
            manga_completed_list = extract_from_lists(
                data["data"].get("mangaCompleted", {}), 10
            )

            return {
                "type": "anime",
                "username": user["name"],
                "days_wasted": days_wasted,
                "total_episodes": animestats["episodesWatched"],
                "anime_watching": anime_watching,
                "anime_completed": anime_completed,
                "anime_watching_list": anime_watching_list,
                "anime_completed_list": anime_completed_list,
                "top_anime_genres": [g["genre"] for g in animestats.get("genres", [])],
                "favorite_anime": extract_titles(user["favourites"]["anime"]["nodes"]),
                "chapters_read": mangastats["chaptersRead"],
                "volumes_read": mangastats["volumesRead"],
                "manga_reading": manga_reading,
                "manga_completed": manga_completed,
                "manga_reading_list": manga_reading_list,
                "manga_completed_list": manga_completed_list,
                "top_manga_genres": [g["genre"] for g in mangastats.get("genres", [])],
                "favorite_manga": extract_titles(user["favourites"]["manga"]["nodes"]),
                "profile_url": user["siteUrl"],
            }
        except Exception as e:
            print(f"AniList service error: {e}")
            return {}
