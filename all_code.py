
import os
import threading
from datetime import datetime

import cv2 as cv
import requests
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()
tg_token = os.getenv("OZSV")
chat_id = os.getenv("CID")



CONFIDENCE_THRESHOLD = 0.80
ON_DETECTED_MESSAGE = "Person detected!"
ON_LEFT_MESSAGE = "Person left.\nStayed for:"

model = YOLO("yolo11n.pt")
cap = cv.VideoCapture("/dev/video2")


system_detected_person = False
missing_counter = 0
person_entered_at = None



def get_datetime():
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime 


def format_duarion(duration):

    total_seconds = int(duration.total_seconds())

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds} s"

# NOTE
# list all devices. Note the (>0 are microphones)
# print(sd.query_devices()) 


def record_and_save_audio(duration, filename="detected.wav"):

    SAMPLE_RATE = 44100   # Hz

    try: 
        print("Recording...")

        recording = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        print("Finished.")

        sf.write(filename, recording, SAMPLE_RATE)

        print("done")

        return True

    except Exception as e:
        print(f"Error: couldn't recored due to {e}")
        return False


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
        print(response.text) # for logs
        return True 

    except requests.exceptions.RequestException as e:
        print(f"Request Error (message wasn't sent): {e}")
        return False
    except Exception as e:
        print(f"Unxpected Error (something went wrong): {e}")
        return False

def voice_handler():
    if record_and_save_audio(15):
        send_voice_record(message="A voice recording after detection")

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
        print(response.text) # for logs
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
        # print(response.text) # for logs
        return True 

    except requests.exceptions.RequestException as e:
        print(f"Request Error (message wasn't sent): {e}")
        return False
    except Exception as e:
        print(f"Unxpected Error (something went wrong): {e}")
        return False



if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

# Verify the actual resolution set
width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
print(f"Actual Resolution: {width}x{height}")
print("FPS:", cap.get(cv.CAP_PROP_FPS))





while True:

    
    ret, frame = cap.read()

    if not ret: # if the value is False (no frame detected) 
        print("Error: Failed to grab frame")
        break


    person_is_present = False

    # set verbose to True or remove it to see logs.
    # classes[0] means a person
    resluts = model.predict(frame,verbose=False, classes=[0])

    for result in resluts:
        for box in result.boxes:

            confidance = box.conf.item()

            if confidance > CONFIDENCE_THRESHOLD:

                # set state
                person_is_present = True


                # draw a box and lable it.
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                cv.rectangle(frame,(x1, y1), (x2, y2), (0,255,0),2)

                cv.putText(
                frame,
                    f"Person {confidance * 100:.1f}%",
                org=(x1,y1 -10),
                color=(66,0,66),
                fontFace=cv.FONT_HERSHEY_SIMPLEX,
                fontScale=1
                )


    if person_is_present:
        missing_counter = 0
    else:
        missing_counter += 1


    # print(f"Present={person_is_present}, Missing={missing_counter}")

    if not system_detected_person and person_is_present:

        system_detected_person = True

        person_entered_at = datetime.now()
        cv.imwrite("person.jpg",frame)
        send_photo(message=ON_DETECTED_MESSAGE)

        threading.Thread(
            target=voice_handler,
            daemon=True
        ).start()

        print("person detected")



        

    elif (system_detected_person and not person_is_present and  missing_counter >= 15):
        
        
        duration = datetime.now() - person_entered_at
        send_on_left(message=ON_LEFT_MESSAGE, duration=format_duarion(duration))
        # print("Person has left") 
        print(f"Person stayed for {format_duarion(duration)}")

        system_detected_person = False
        missing_counter = 0


    cv.imshow("Frame", frame)
    # exit using q key
    if cv.waitKey(33) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()






