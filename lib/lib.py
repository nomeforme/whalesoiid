from litellm import completion, acompletion
from elevenlabs.client import ElevenLabs, AsyncElevenLabs
from elevenlabs import stream, Voice, VoiceSettings, play
from dotenv import load_dotenv
from lib.DeepgramTranscription import DeepgramTranscription
from lib.prompt_context import get_character_description, get_system_message
import os
import socket
import json
import random
from playsound import playsound


# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
# ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

elevenlabs_client = ElevenLabs(
  api_key=ELEVENLABS_API_KEY
)

def think(use_content: str, use_system_message: str = 'donation', message_history: list = [], word_count: str = 100) -> str:

    model_type = 'gpt-4o'

    character_description = get_character_description('whalesoid')

    system_message = get_system_message(
        character_description,
        use_system_message=use_system_message,
        message_history=message_history,
        word_count=word_count,
    )

    messages = [{
        "content": system_message,
        "role": "system"
    },
    {
        "content": use_content,
        "role": "user"
    }]

    response = completion(
        model=model_type, 
        messages=messages, 
        stream=False
    )

    response = response.choices[0].message.content
    return response

def speak(response: str):

    model_type = 'eleven_turbo_v2_5'
    voice_id = 'EuPGJ9gzDyZgMhf6ZIsP'

    audio = elevenlabs_client.generate(
        text=response,
        model=model_type,
        voice=Voice(
            voice_id=voice_id,
            settings=VoiceSettings(
                stability=0.77,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            )
        ),
        stream=False
    )

    play(audio)

def listen(step: int = 0):

    RATE = 16000
    device_index = None
    timeout = 10

    transcription = DeepgramTranscription(sample_rate=RATE, device_index=device_index, timeout=timeout)

    transcription.reset()
    transcription.start_listening(step=step)
    utterance = transcription.get_final_result()

    # print("DEEPGRAM UTTERANCE:", utterance)

    return utterance

def log_response(response: str, file_path: str):

    formatted_response = response.replace('\n', ' ').strip()

    with open(file_path, 'a') as f:
        f.write(f"{formatted_response}\n")

def send_esp_instruction(instruction: str, esp_ip: str = '192.168.1.145', esp_port: int = 1666):

    esp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    esp_socket.sendto(bytes(instruction, 'utf-8'), (esp_ip, esp_port))

def get_random_stimulus():
    with open(os.getcwd()+'/lib/prompts/ocean.json', 'r') as f:
        data = json.load(f)
    stimuli = data['conversation_stimuli']
    stimulus_key = random.choice(list(stimuli.keys()))
    question = stimuli[stimulus_key]['stimulus']
    return question

def play_speech_indicator() -> None:
        
    # get the path to the speech indicator sound
    speech_indicator_path = os.getcwd()+"/media/beep_start.wav"
    playsound(speech_indicator_path, block=False)

def play_speech_acknowledgement(voice_id: str = 'EuPGJ9gzDyZgMhf6ZIsP') -> None:
    random_effect = random.choice([
        'oh', 'um', 'hrm', 'hrmmmmm',
        'okay', 'i see', 'right',
            'ah', 'mhm.', 'ooh', # 'oh, really?'
        'ahh', 'hmm', 
    ])

    file_path = os.path.join(os.getcwd(), "media/runtime_effects", f"{voice_id}_{random_effect}.mp3")
    
    # Check if the file exists before trying to play it
    if os.path.exists(file_path):
        print(f"\n\033[94m{random_effect}\033[0m")
        playsound(file_path, block=False)
        # mixer.init()
        # mixer.music.load(file_path)
        # mixer.music.play(loops=1)
    else:
        # Print a warning message if the file does not exist
        print("\033[90m\nThe specified audio effect file does not exist. Skipping playback.\033[0m")