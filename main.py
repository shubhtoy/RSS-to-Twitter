import schedule
import gspread
import pandas as pd
import random
from util import rss_to_twitter
import time
from Config import Config as conf
gc = gspread.service_account(filename="secret.json")

config=conf()

def rss():
    # getting data from google sheet
    sheet = gc.open("Crypto")
    worksheet = sheet.sheet1
    dataframe = pd.DataFrame(worksheet.get_all_records())

    all_links = dataframe["RSS"].to_list()
    # getting a random element from the given array of rss links
    all_links = (random.sample(all_links, 1))[0]
    rss_to_twitter(all_links)
    return


schedule.every(conf.time_interval).seconds.do(rss)
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
