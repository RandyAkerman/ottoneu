import os
import pandas as pd
from constants import STATS
from selenium.webdriver.common.by import By


def get_roster():

    league_number = os.getenv("LEAGUE_NUMBER")

    url = f"https://ottoneu.fangraphs.com/{league_number}/rosterexport"

    league_roster = pd.read_csv(url)

    team_number = int(os.getenv("TEAM_NUMBER"))
    team_roster = league_roster.loc[
        (league_roster.TeamID == team_number)
        & (league_roster["FG MajorLeagueID"].notnull())
    ]

    return team_roster


def login(driver):
    """Log into FanGraphs.com using selenium

    Args:
        driver (selenium.webdriver): Active connection to a browser using a selenium.webdriver object
    """
    url = f"https://blogs.fangraphs.com/wp-login.php?redirect_to=https://www.fangraphs.com/"

    driver.get(url)

    account = driver.find_element(By.ID, "user_login")

    account.send_keys(os.getenv("FANGRAPHS_USER"))

    pw = driver.find_element(By.ID, "user_pass")

    pw.send_keys(os.getenv("FANGRAPHS_PASS"))

    driver.find_element(By.ID, "wp-submit").click()


def clean_roster(roster):
    # TODO: Remove players who are not eligible to play
    # TODO: Clean up column names, i.e slugify
    roster["name_slug"] = roster.Name.str.lower().str.replace(" ", "-", regex=False)
    # TODO: Need to clean this up, the trailing decimal .0 is causing problems in a merge.  Probably a more efficient way to remove that
    roster["FG MajorLeagueID"] = (
        roster["FG MajorLeagueID"].astype("int").astype("string")
    )

    roster.Salary = roster.Salary.replace({",": "", "\$": ""}, regex=True).astype(
        "float"
    )

    return roster
