import os
from typing import Optional

from requests import Session

from signin import signin
from time import sleep


class GeoguessrSession:
    __build_id: str
    __token: str

    def __init__(self, token: str, build_id: str):
        self.__token = token
        self.__build_id = build_id

    def __create_session(self):
        session = Session()
        session.cookies.set("_ncfa", self.__token, domain="www.geoguessr.com")
        session.headers = {"Content-Type": "application/json"}
        return session

    def get_party(self) -> [str, str]:
        """ Returns Party id """
        party = \
            self.__create_session().get(f"https://www.geoguessr.com/_next/data/{self.__build_id}/en/party.json").json()[
                "pageProps"][
                "party"]

        return [party["partyId"],party["joinCode"]["code"]]

    def apply_settings(self, rounds: Optional[int] = 5, round_length: Optional[int] = 60):
        resp = self.__create_session().put("https://www.geoguessr.com/api/v4/parties/v2/game-settings",
                           data={"forbidMoving": False, "forbidZooming": False, "forbidRotating": False,
                                 "roundTime": round_length, "mapSlug": "world", "roundCount": rounds})
        print(resp.status_code)
        print(resp.text)

    def start_game(self, party_id: str):
        resp = self.__create_session().post(f"https://game-server.geoguessr.com/api/parties/v2/{party_id}/lobby", data={})
        print(resp.status_code)
        print(resp.text)

    def next_round(self, party_id: str, game_round: int):
        self.__create_session().post(f"https://game-server.geoguessr.com/api/live-challenge/{party_id}/advance-round", data={"toRoundNumber": game_round})

if __name__ == "__main__":
    sesh = GeoguessrSession(**signin(os.environ.get("GEOGUESSR_EMAIL"), os.environ.get("GEOGUESSR_PWD")))

    party_id, join_code = sesh.get_party()

    sesh.apply_settings()

    print(f"Created party {party_id}")
    print(f"https://www.geoguessr.com/join/{join_code}")

    sleep(60)

    print("Starting game...")

    sesh.start_game(party_id)

    for game_round in range(2, 5):
        sleep(75)
        print(f"Starting round {game_round}...")
        sesh.next_round(party_id, game_round)
