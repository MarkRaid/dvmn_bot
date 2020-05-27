import requests
import pprint
import telegram
import time
import os
import logging

bot = telegram.Bot(token=os.getenv("TELEGRAM_TOKEN"))

USER_REVIEWS_URL = "https://dvmn.org/api/long_polling/"

headers = {
  "Authorization": f"Token {os.getenv('DVMN_API_TOKEN')}"
}


logging.basicConfig(level=logging.INFO)
logging.info('Бот запущен')


def get_new_reviews(headers={}, params={}):
    response = requests.get(USER_REVIEWS_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

timestamp = ""

while True:
  try:
    response_data = get_new_reviews(headers=headers, params={"timestamp": timestamp})
  except requests.exceptions.ReadTimeout:
    continue
  except requests.exceptions.ConnectionError:
    time.sleep(12)
    continue

  if response_data["status"] == "timeout":
    timestamp = response_data["timestamp_to_request"]
  elif response_data["status"] == "found":
    attempt = response_data["new_attempts"][0]
    
    header_text   = f'У вас проверили работу ["{attempt["lesson_title"]}"](https://dvmn.org{attempt["lesson_url"]})"'
    positive_text = "Преподавателю всё понравилось, можно приступать к следующему уроку"
    negative_text = "К сожалению, в работе нашлись ошибки"
    footer_text   = negative_text if attempt["is_negative"] else positive_text
    message       = header_text + '\n\n' + footer_text
    
    bot.send_message(
      chat_id=os.getenv("CHAT_ID"),
      text=message,
      parse_mode=telegram.ParseMode.MARKDOWN
    )

    timestamp = response_data["last_attempt_timestamp"]