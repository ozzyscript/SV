import requests
from utils import get_datetime
from dotenv import load_dotenv
import os

load_dotenv()

tg_token = os.getenv("OZSV")
chat_id = os.getenv("CID")


def send_voice_record(message):

    try:
        with open("detected.wav", "rb") as audio:

            files = { "voice": audio }

            detected_at = get_datetime()
            url = f"https://api.telegram.org/bot{tg_token}/sendVoice"
            data = {
                "chat_id": chat_id,
                "caption": f"{message}\n{detected_at}",

            }

            response = requests.post(url, data=data,files=files, timeout=5)
        response.raise_for_status()
        return True 

    except requests.exceptions.RequestException as e:
        print(f"Request Error (message wasn't sent): {e}")
        return False
    except Exception as e:
        print(f"Unxpected Error (something went wrong): {e}")
        return False




def send_photo(message):

    try:
        with open("person.jpg", "rb") as image:

            files = { "photo": image }

            detected_at = get_datetime()
            url = f"https://api.telegram.org/bot{tg_token}/sendPhoto"
            data = {
                "chat_id": chat_id,
                "caption": f"{message}\n{detected_at}",

            }

            response = requests.post(url, data=data,files=files, timeout=5)
        response.raise_for_status()

        return True 

    except requests.exceptions.RequestException as e:
        print(f"Request Error (message wasn't sent): {e}")
        return False
    except Exception as e:
        print(f"Unxpected Error (something went wrong): {e}")
        return False



def send_on_left(message,duration):

    try:
        

        url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": f"{message}\n{duration}",
        }
        response = requests.post(url, json=data, timeout=5)
        response.raise_for_status()

        return True 

    except requests.exceptions.RequestException as e:
        print(f"Request Error (message wasn't sent): {e}")
        return False
    except Exception as e:
        print(f"Unxpected Error (something went wrong): {e}")
        return False

