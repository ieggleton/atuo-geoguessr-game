""" Runs the script(s) locally"""
import os
from time import sleep

from geoguessr_session import GeoguessrSession
from signin import signin

if __name__ == "__main__":
    sesh = GeoguessrSession(**signin(os.environ.get("GEOGUESSR_EMAIL"), os.environ.get("GEOGUESSR_PWD")))

    party_id, join_code = sesh.get_party()

    sesh.apply_settings()

    print(f"Created party {party_id}")
    print(f"https://www.geoguessr.com/join/{join_code}")

    sleep(60)

    print("Starting game...")

    game_id = sesh.start_game(party_id)

    for game_round in range(2, 5 + 1):
        sleep(75)
        print(f"Starting round {game_round}...")
        sesh.next_round(game_id, game_round)
