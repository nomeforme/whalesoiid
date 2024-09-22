import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from dotenv import load_dotenv

load_dotenv()

client_eleven = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

utterances = ["oh", "oh.", "oh?", "um", "hrm", "hrmmmmm", "go on", "ugh", "uh", "uh?", "eh?", "interesting!", "yeah?", "yes?", "okay", "sure thing.", "i see", "right", "really?", "really.", "oh, really?", "ah", "mhm.", "ooh", "ahh", "hmm", "huh.", "huh!", "huh??", "kay."]
voice_id = 'EuPGJ9gzDyZgMhf6ZIsP'

def generate_and_save_audios():
    for utterance in utterances:
        filepath = os.path.join(os.getcwd(), f'media/runtime_effects/{voice_id}_{utterance}.mp3')
        if not os.path.exists(filepath):  # Check if the file already exists
            audio = client_eleven.generate(
                text=utterance,
                model="eleven_turbo_v2",
                voice=voice_id,
                stream=True
            )
            save(audio, filepath)
            print(f"\033[32mAudio file saved: {filepath}\033[0m")
        else:
            print(f"\033[91mFile already exists and was not regenerated: {filepath}\033[0m")

generate_and_save_audios()