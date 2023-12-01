import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import time

import os
import environ

env = environ.Env()
environ.Env.read_env()

# Программа отслеживает конкретного человека в конкретном чате Discord и как только он пишет сообщение 
# оно копируется и отправляется в этот чат, а затем программа закрывается. Можно настроить чтобы программа 
# не закрывалась после одного сообщения
# Также лучше не ставить TRACK_FOREVER и свой ник, программа не будет корректно работать

TARGET = os.getenv("TARGET")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
CHAT_LINK = os.getenv("CHAT_LINK")
DELAY = 0.01
TRACK_FOREVER = False

def send_chat_message(message, input_field):
    pyperclip.copy(message)
    input_field.click()
    input_field.send_keys(Keys.CONTROL, 'v')
    input_field.send_keys(Keys.ENTER)
    print('Message sent: ' + message)


def get_message_id(message):
    children = message.find_elements(By.XPATH, "./*")
    if len(children) < 3:
        return None
    return children[2].get_attribute('id')


def get_last_message_id(driver):
    messages = driver.find_elements(By.CSS_SELECTOR, '.contents_f41bb2')
    for message in reversed(messages):
        children = message.find_elements(By.XPATH, "./*")
        if len(children) < 3:
            continue
        return children[2].get_attribute('id')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Discord chat bot.')
    parser.add_argument('--target_username', type=str, default=TARGET,
                        help='Target username to track.')  # Target username to track
    parser.add_argument('--login', type=str, default=LOGIN, help='Login for discord.')  # Login for discord
    parser.add_argument('--password', type=str, default=PASSWORD, help='Password for discord.')  # Password for discord
    parser.add_argument('--chat_link', type=str,
                        default=CHAT_LINK,
                        help='Discord chat link.')  # Discord chat link
    parser.add_argument('--delay', type=float, default=DELAY,
                        help='Delay of refreshing messages.')  # Delay of refreshing messages

    args = parser.parse_args()

    USERNAME = args.target_username
    LOGIN = args.login
    PASSWORD = args.password
    CHAT_LINK = args.chat_link
    DELAY = args.delay

    print('Target Username: ' + USERNAME)
    print('Chat link: ' + CHAT_LINK)
    print('Delay: ' + str(DELAY))

    driver = webdriver.Chrome()
    driver.get(CHAT_LINK)
    
    wait = WebDriverWait(driver, 10)
    buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[type="button"]')))
    buttons[1].click()
    driver.find_element(By.ID, 'uid_5').send_keys(LOGIN)
    driver.find_element(By.ID, 'uid_7').send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
    
    messages_list = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.scrollerInner__059a5'))
    )
    input_field = driver.find_element(By.CSS_SELECTOR, '[role="textbox"]')
    end = False
    last_message_id = get_last_message_id(driver)
    print('Start listening' + ' ' + str(last_message_id))
    while not end:
        messages = driver.find_elements(By.CSS_SELECTOR, '.contents_f41bb2')
        for message in reversed(messages):
            children = message.find_elements(By.XPATH, "./*")
            if len(children) < 3:
                continue
            message_id = get_message_id(message)
            # print(message_id, ' | ', last_message_id)
            if message_id == last_message_id:
                break
            message_text = children[2].text
            children2 = children[1].find_elements(By.XPATH, "./*")
            username = children2[0].text
            print('Message received: ' + message_text)
            if username == USERNAME:
                send_chat_message(message_text, input_field)
                if not TRACK_FOREVER:
                    end = True
        time.sleep(DELAY)
    print('End listening')
