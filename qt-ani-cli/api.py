import requests
import json
import sys


class AniCliAPI:
    def __init__(self, mode="sub"):
        self.api_url = "https://api.allanime.day/api"
        self.referer = "https://allmanga.to"
        self.agent   = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        self.mode = mode

    def _headers(self):
        return {"Referer": self.referer, "User-Agent": self.agent}

    def search_anime(self, query):
        gql = '''query($search:SearchInput $limit:Int $page:Int
                       $translationType:VaildTranslationTypeEnumType
                       $countryOrigin:VaildCountryOriginEnumType){
            shows(search:$search limit:$limit page:$page
                  translationType:$translationType countryOrigin:$countryOrigin){
                edges{ _id name availableEpisodes thumbnail type __typename }
            }
        }'''
        variables = {
            "search": {"allowAdult": False, "allowUnknown": False, "query": query},
            "limit": 40, "page": 1,
            "translationType": self.mode,
            "countryOrigin": "ALL"
        }
        try:
            r = requests.get(self.api_url,
                             params={"variables": json.dumps(variables), "query": gql},
                             headers=self._headers())
            r.raise_for_status()
            edges = r.json().get("data", {}).get("shows", {}).get("edges", [])
            return [
                {
                    "id":        s["_id"],
                    "title":     s["name"],
                    "episodes":  s.get("availableEpisodes", {}).get(self.mode, 0),
                    "thumbnail": s.get("thumbnail") or "",
                    "type":      s.get("type") or "",
                }
                for s in edges if s
            ]
        except Exception as e:
            print(f"[api] search error: {e}")
            return []

    def get_episodes(self, show_id):
        gql = '''query($showId:String!){
            show(_id:$showId){ _id availableEpisodesDetail }
        }'''
        try:
            r = requests.get(self.api_url,
                             params={"variables": json.dumps({"showId": show_id}), "query": gql},
                             headers=self._headers())
            r.raise_for_status()
            eps = r.json().get("data", {}).get("show", {}) \
                          .get("availableEpisodesDetail", {}).get(self.mode, [])
            return sorted([e for e in eps if e.replace(".", "", 1).isdigit()], key=float)
        except Exception as e:
            print(f"[api] episodes error: {e}")
            return []
