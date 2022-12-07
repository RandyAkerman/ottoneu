from utils import login, get_roster, clean_roster
import os
import glob
import time
from datetime import date
import pandas as pd
import numpy as np
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from constants import VALUATION_DOWNLOAD_BUTTON, VALUATION_PITCHERS, VALUATION_BATTERS, VALUATION_OTTONEU_4x4_PRESET,VIBBER_GOOGLESHEET_ID, VIBBER_GOOGLESHEET_TAB

def valuation():
    # get_fangraphs_auction_values()
    get_vibber_values(VIBBER_GOOGLESHEET_ID, VIBBER_GOOGLESHEET_TAB)
    pitchers = surplus_calculator(player_type='pitchers')
    batters = surplus_calculator(player_type='batters')
    valuation = {'date': date.today().strftime("%Y-%m-%d"),
                 'team_name': batters[1]['Team Name'],
                 'batters': batters,
                 'pitchers': pitchers
                 }
    return(valuation)

# TODO: Be able to pass in argument to plug into surplus calculator URL (keepers, league format, etc)
def get_fangraphs_auction_values():

    # remove existing auction calculator files
    for f in glob.glob(os.getenv("VALUATION_PATH")+"fangraphs-auction-calculator*.csv"):
        os.remove(f)

    service = Service(executable_path=os.getenv("CHROME_PATH"))
    options = webdriver.ChromeOptions()

    prefs = {"download.default_directory" : os.getenv("VALUATION_PATH")}

    options.add_experimental_option("prefs",prefs)
    # options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)

    login(driver)

    url = f"https://www.fangraphs.com/fantasy-tools/auction-calculator"

    driver.get(url)
    # select preset for ottoneu 4x4
    driver.find_element(By.XPATH, VALUATION_OTTONEU_4x4_PRESET).click()

    time.sleep(5)
    driver.find_element(By.XPATH,VALUATION_BATTERS).click()
    time.sleep(5)
    driver.find_element(By.XPATH,VALUATION_DOWNLOAD_BUTTON).click()
    time.sleep(5)
    os.rename(os.path.join(os.getenv("VALUATION_PATH"),f"fangraphs-auction-calculator.csv"),
                os.path.join(os.getenv("VALUATION_PATH"),f"fangraphs-auction-calculator-batters.csv"))

    # Pitcher valuations
    driver.find_element(By.XPATH,VALUATION_PITCHERS).click()
    time.sleep(5)
    driver.find_element(By.XPATH,VALUATION_DOWNLOAD_BUTTON).click()
    time.sleep(5)
    os.rename(os.path.join(os.getenv("VALUATION_PATH"),f"fangraphs-auction-calculator.csv"),
                os.path.join(os.getenv("VALUATION_PATH"),f"fangraphs-auction-calculator-pitchers.csv"))

    driver.close()

def get_vibber_values(sheet_id, sheet_name):
    # TODO: Get this cleaned up and merged into the dictionary
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    values = pd.read_csv(url,usecols=[0,1,3,4]) #

    # values.dropna(axis=1, how="all", inplace=True)

    values.rename(columns={"$":"value"}, inplace=True)

    values.dropna(axis=0,how="any", inplace=True)

    values.otto = values.otto.astype("int")

    values.drop(axis=1, columns=["Name", "Team"], inplace=True)

    return(values)
# TODO: Convert csv into json for report
def surplus_calculator(player_type):
    """_summary_

    Args:
       
    """
        
    if player_type == 'batters':
        # Read in fangraphs valuation csv
        valuation = pd.read_csv(os.path.join(os.getenv("VALUATION_PATH"),f"fangraphs-auction-calculator-batters.csv"),
                                usecols = ['PA', 'mR', 'mHR', 'mOBP', 'mSLG', 'PTS', 'aPOS', 'Dollars', 'PlayerId'])
    else:
        valuation = pd.read_csv(os.path.join(os.getenv("VALUATION_PATH"),f"fangraphs-auction-calculator-pitchers.csv"),
                                usecols = ['IP','mERA','mWHIP','mSO','mHR','PTS','aPOS','Dollars','PlayerId'])
    # Read in current Ottoneu roster
    _roster_ = get_roster()

    roster = clean_roster(_roster_)
    # Merge together

    compare_value = valuation.merge(roster, how="inner", left_on="PlayerId", right_on="FG MajorLeagueID")
    # Calculate difference between current salary and valuation
    compare_value['delta'] = compare_value.Dollars - compare_value.Salary
    # Tag players with keep or cut
    compare_value["action"] = 'keep'
    compare_value.loc[(compare_value['delta'] < 0), 'action'] = 'cut'

    value_dict = compare_value.to_dict(orient='records')

    return(value_dict)

if __name__ == '__main__':
    valuation()