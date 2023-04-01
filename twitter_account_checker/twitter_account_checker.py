from bs4 import BeautifulSoup
from discord import SyncWebhook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import logging

from secrets import secrets

# configure constants
handle = secrets['handle']
twitter_url = "https://twitter.com/" + handle

# configure logging
logging.basicConfig(
    filename='twitter_account_checker.log',
    format='%(asctime)s | %(message)s',
    level=logging.INFO
)


def scrape_twitter(desired_handle, url):
    # print('configuring webdriver')
    options = Options()
    options.set_preference('javascript.enabled', True)
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)

    # print('getting page')
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//div[@data-testid="primaryColumn"]'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        print(e)
    driver.quit()

    message = None
    if "this account doesn't exist" in soup.text.lower():
        message = f'Heads up! The handle [{desired_handle}](https://twitter.com/{desired_handle}) might be free! [' \
                  f'Sign up here.](https://twitter.com/i/flow/signup)'

    elif "account suspended" in soup.text.lower():
        logging.info("account still suspended")
    else:
        print('Scraping Error???')

    return message


def send_discord_message(message):
    discord_webhook = SyncWebhook.from_url(secrets['discord webhook'])
    discord_webhook.send(message)


def main():
    message = scrape_twitter(handle, twitter_url)
    if message is not None:
        send_discord_message(message)
        logging.info("message sent to discord")


if __name__ == '__main__':
    main()
