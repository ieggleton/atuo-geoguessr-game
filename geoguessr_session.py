from typing import Optional

from requests import Session


class GeoguessrSession:
    __build_id: str
    __token: str

    def __init__(self, token: str, build_id: str):
        self.__token = token
        self.__build_id = build_id
        self.__session = Session()
        self.__session.cookies.set("_ncfa", self.__token, domain=".geoguessr.com")

    def get_party(self) -> [str, str]:
        """ Returns Party id and joining code"""
        party = \
            self.__session.get(f"https://www.geoguessr.com/_next/data/{self.__build_id}/en/party.json").json()[
                "pageProps"][
                "party"]

        return [party["partyId"], party["joinCode"]["code"]]

    def apply_settings(self, rounds: Optional[int] = 5, round_length: Optional[int] = 60):
        """ Apply settings to the party"""
        self.__session.put("https://www.geoguessr.com/api/v4/parties/v2/game-settings",
                                           json={"forbidMoving": False, "forbidZooming": False, "forbidRotating": False,
                                                 "roundTime": round_length, "mapSlug": "world", "roundCount": rounds},
                                           headers={"Content-Type": "application/json"})

    def start_game(self, party_id: str):
        """ API call to start the game"""
        resp = self.__session.post(f"https://game-server.geoguessr.com/api/parties/v2/{party_id}/lobby",
                                            json={},
                                            headers={"Content-Type": "application/json"})
        return resp.json()["gameLobbyId"]

    def next_round(self, game_id: str, game_round: int):
        """ API Call to go to next round"""
        self.__session.post(f"https://game-server.geoguessr.com/api/live-challenge/{game_id}/advance-round",
                                     json={"toRoundNumber": game_round},
                                     headers={"Content-Type": "application/json"})
