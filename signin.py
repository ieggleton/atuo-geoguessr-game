""" Handles sign in to Geoguessr, gets the ncfa token for future calls
which will be done via API"""
import json
import os
from time import sleep

from selenium.webdriver.common.by import By
from seleniumbase import SB


def signin(user: str, password: str) -> dict[str, str]:
    """ Do sign in and return ncfa token"""
    with SB(uc=True, xvfb=True if os.getenv("CONTAINERISED") == "true" else False) as driver:
        driver.uc_open_with_reconnect("https://nowsecure.nl", reconnect_time=6)
        driver.save_screenshot("/app/screeenshots/wtf3.png")

        driver.uc_open_with_reconnect("https://www.geoguessr.com/signin", reconnect_time=6)

        try:
            driver.find_element(By.ID, "accept-choices").click()
        except:
            pass

        driver.find_element(By.NAME, 'email').send_keys(user)
        driver.find_element(By.NAME, 'password').send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        driver.save_screenshot("/app/screeenshots/wtf2.png")

        sleep(2)

        ncfas = [cookie for cookie in driver.get_cookies() if cookie["name"] == "_ncfa"]

        next_data = json.loads(driver.find_element(By.ID, "__NEXT_DATA__").get_attribute("innerHTML"))

        return {
            "token": ncfas[0]["value"],
            "build_id": next_data["buildId"]
        }
