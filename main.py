from datetime import datetime
import cv2 as cv
from ultralytics import YOLO
from dotenv import load_dotenv
import os
import threading
from tg_utils import send_on_left, send_photo
from utils import format_duration
from audio_utils import voice_handler



load_dotenv()
tg_token = os.getenv("OZSV")
chat_id = os.getenv("CID")

model = YOLO("yolo11n.pt")
cap = cv.VideoCapture("/dev/video2")

CONFIDENCE_THRESHOLD = 0.80
ON_DETECTED_MESSAGE = "Person detected!"
ON_LEFT_MESSAGE = "Person left.\nStayed for:"

system_detected_person = False
missing_counter = 0
person_entered_at = None


if not cap.isOpened():
    print("Error: Could not open camera")
    exit()


# Verify the actual resolution set
# width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
# height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
# print(f"Actual Resolution: {width}x{height}")
# print("FPS:", cap.get(cv.CAP_PROP_FPS))

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

    elif (
            system_detected_person and not 
            person_is_present and  
            missing_counter >= 15
        ):
        
        
        duration = datetime.now() - person_entered_at
        send_on_left(message=ON_LEFT_MESSAGE, duration=format_duration(duration))


        system_detected_person = False
        missing_counter = 0


    cv.imshow("Frame", frame)
    # exit using q key
    if cv.waitKey(33) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()



