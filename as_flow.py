""" Runs everything as a prefect flow"""
from argparse import ArgumentParser
from time import sleep
from typing import Optional

from prefect import flow, task, get_run_logger
from prefect.blocks.system import Secret
from prefect_slack import SlackWebhook
from prefect_slack.messages import send_incoming_webhook_message

from geoguessr_session import GeoguessrSession
from signin import signin

__SLACK_MESSAGE = """
:sirens: *GEOGUESSR GAME IN 5 MINUTES* :sirens:

@here This is your 5 minute warning for Geoguessr

Please join the game here: {url}

THE GAME WILL START IN 5 MINUTES
"""


@task
def finish_round(session: GeoguessrSession, party_id: str, rnd: int):
    """ Finish the current round by going to the next one"""
    session.next_round(party_id, rnd + 1)


@task
def start_game(session: GeoguessrSession, party_id: str):
    """ Start the game"""
    session.start_game(party_id)


@task
def create_party(session: GeoguessrSession, rounds: Optional[int], round_length: Optional[int]):
    """ Create a party game and apply settings"""
    party_id, join_code = session.get_party()
    session.apply_settings(rounds, round_length)

    send_incoming_webhook_message(
        slack_credentials=SlackWebhook.load("geoguessr_webhook"),
        text=__SLACK_MESSAGE.format(url=f"https://www.geoguessr.com/join/{join_code}")
    )

    return party_id


@task
def sign_in(email: str):
    """ Signin using stored credential"""
    pwd = Secret.load("geoguessr_password")
    return signin(email, pwd.get())


@flow(name="Geoguessr Game")
def geoguessr_game(email: str, rounds: Optional[int], round_length: Optional[int]):
    """ Run the whole game"""
    logger = get_run_logger()
    logger.info(f"Sign in to geoguessr with email {email}")
    token, next_id = sign_in(email)

    sesh = GeoguessrSession(token, next_id)

    logger.info("Creating new party")
    party_id = create_party(sesh, rounds, round_length)

    logger.info("Giving players 5 minutes to join")
    sleep(300)

    logger.info("Let's get this party started")
    start_game()

    for rnd in range(1, rounds):
        logger.info(f"Waiting {round_length + 15} to start next round...")
        sleep(round_length + 15)
        logger.info("Start next round")
        finish_round(party_id, rnd)

    logger.info("End of game")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--email", required=True, help="Email address of party owner")
    parser.add_argument("--rounds", required=False, help="Number of rounds", default=5)
    parser.add_argument("--round-length", required=False, help="Length of round in seconds", default=60)

    geoguessr_game(**parser.parse_args())
