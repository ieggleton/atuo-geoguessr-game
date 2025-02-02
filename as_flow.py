from typing import Optional


from argparse import ArgumentParser

from time import sleep
from prefect import flow, task
from prefect.blocks.system import Secret

from geoguessr_session import GeoguessrSession
from signin import signin

from prefect_slack import SlackCredentials, SlackWebhook
from prefect_slack.messages import send_chat_message, send_incoming_webhook_message

__SLACK_MESSAGE="""
:sirens: *GEOGUESSR GAME IN 5 MINUTES* :sirens:

@here This is your 5 minute warning for Geoguessr

Please join the game here: {url}

THE GAME WILL START IN 5 MINUTES
"""

@task
def finish_round(session: GeoguessrSession, party_id: str, rnd: int):
    session.next_round(party_id, rnd + 1)

@task
def start_game(session: GeoguessrSession, party_id: str):
    session.start_game(party_id)

@task
def create_party(session: GeoguessrSession, rounds: Optional[int], round_length: Optional[int]):
    party_id, join_code = session.get_party()
    session.apply_settings(rounds, round_length)

    send_incoming_webhook_message(
        slack_credentials=SlackWebhook.load("geoguessr_webhook"),
        text=__SLACK_MESSAGE.format(url=f"https://www.geoguessr.com/join/{join_code}")
    )

    return party_id

@task
def sign_in(email: str):
    pwd = Secret.load("geoguessr_password")
    return signin(email, pwd.get())


@flow(name="Geoguessr Game")
def geoguessr_game(email: str, rounds: Optional[int], round_length: Optional[int]):
    token, next_id = sign_in(email)

    sesh = GeoguessrSession(token, next_id)

    party_id = create_party(sesh, rounds, round_length)

    sleep(300)
    start_game()

    for rnd in range(1, rounds):
        sleep(round_length + 15)
        finish_round(party_id, rnd)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--email", required=True, help="Email address of party owner")
    parser.add_argument("--rounds", required=False, help="Number of rounds", default=5)
    parser.add_argument("--round-length", required=False, help="Length of round in seconds", default=60)

    geoguessr_game(**parser.parse_args())