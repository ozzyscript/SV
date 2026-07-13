from tg_utils import send_voice_record
import sounddevice as sd
import soundfile as sf


# NOTE
# list all devices.(>0 are microphones)
# print(sd.query_devices()) 

def record_and_save_audio(duration, filename="detected.wav"):

    SAMPLE_RATE = 44100   # Hz

    try: 
        # print("Recording...")

        recording = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        # print("Finished.")

        sf.write(filename, recording, SAMPLE_RATE)

        # print("done")

        return True

    except Exception as e:
        print(f"Error: couldn't recored due to {e}")
        return False


def voice_handler():

    if record_and_save_audio(15):
        send_voice_record(message="A voice recording after detection")
