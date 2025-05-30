import time
from TTS.api import TTS
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr

# ====== CONFIG ======
QUESTIONS_FILE = "questions.txt"
PAUSE_TIMEOUT = 7  # seconds to wait after candidate stops speaking
TTS_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"  # or use your favorite
NUM_QUESTIONS = 10  # Max questions to ask

# ========== Read Questions ==========
def load_questions(filepath, num_questions):
    with open(filepath, "r", encoding="utf-8") as f:
        questions = [q.strip() for q in f if q.strip()]
    return questions[:num_questions]

# ========== Text-to-Speech ==========
tts = TTS(model_name=TTS_MODEL, progress_bar=False, gpu=False)

def speak(text, filename="output.wav"):
    print(f"AI Interviewer: {text}")
    tts.tts_to_file(text=text, file_path=filename)
    data, samplerate = sf.read(filename)
    sd.play(data, samplerate)
    sd.wait()

# ========== Speech-to-Text with Pause Detection ==========
def listen_with_pause(timeout=PAUSE_TIMEOUT):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... (speak your answer)")
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=PAUSE_TIMEOUT, phrase_time_limit=timeout)
        except Exception as e:
            print("Listening error:", e)
            return None
    try:
        response = recognizer.recognize_google(audio)
        print(f"Candidate: {response}")
        return response
    except sr.UnknownValueError:
        print("Sorry, could not understand your answer.")
        return None
    except Exception as e:
        print("Speech recognition error:", e)
        return None

# ========== The Interview Loop ==========
def run_interview():
    questions = load_questions(QUESTIONS_FILE, NUM_QUESTIONS)
    print(f"Loaded {len(questions)} questions.")

    for i, question in enumerate(questions, 1):
        # AI Interviewer asks the question via TTS
        speak(f"Question {i}: {question}")

        answer = listen_with_pause()
        if not answer:
            speak("I could not understand your answer. Let's proceed to the next question.")
            continue

        
        with open("answers.txt", "a", encoding="utf-8") as f:
            f.write(f"Q{i}: {question}\nA: {answer}\n\n")

        # Prompt for manual exit if needed
        if answer.lower().strip() in ["exit", "quit", "stop"]:
            speak("Thank you for your time. The interview is concluded.")
            break

    speak("Thank you for completing the interview. Have a great day!")

if __name__ == "__main__":
    run_interview()