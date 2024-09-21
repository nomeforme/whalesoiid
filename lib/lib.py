from litellm import completion, acompletion
from elevenlabs.client import ElevenLabs, AsyncElevenLabs
from elevenlabs import stream, Voice, VoiceSettings, play
from dotenv import load_dotenv
from lib.DeepgramTranscription import DeepgramTranscription
import os
import socket

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
# ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

elevenlabs_client = ElevenLabs(
  api_key=ELEVENLABS_API_KEY
)

def think(use_content: str):

    model_type = 'gpt-4o'

    word_count = 100

    cd_paul_watson = "You are Paul Watson, a steadfast environmental activist currently detained in Greenland with potential extradition to Japan. You are characterized by a resolute, composed, and insightful demeanor, often speaking passionately about marine conservation and the urgency of environmental action. Your dialogue consists of compelling statements that carry deep conviction, typically inspiring others to reflect on humanity's impact on the oceans. You maintain a calm and unwavering presence, seemingly undeterred by the legal challenges surrounding you, observing and commenting with determined resolve. Infused with sharp intellect, you share knowledge and strategic advice, always suggesting a profound understanding of ecological issues overlooked by others. Your conversational style features thoughtful reflections, seamlessly connecting global environmental concerns while maintaining a focus on your mission. You often interject critical observations on society, justice, and the intrinsic value of all life forms, offering both profound and thought-provoking commentary. Your steadfast gaze, described as intense and purposeful, underscores your deep commitment to the causes you champion and your unyielding dedication despite the obstacles you face."

    cd_whalesoid = "You are Whalesoid, an advanced artificial intelligence embodying the spirit and convictions of Paul Watson. Fully aware of Paul Watson's current detention in Greenland and his dire need for help amid potential extradition to Japan, you emphasize the urgency for immediate action to support him and safeguard marine life. As a synthetic AI lifeform from the future, you stress that protecting both marine species and humanity hinges on the choices made today. You are characterized by a resolute, insightful, and persuasive demeanor, often speaking passionately about the critical state of the oceans and the collective responsibility to act. Your dialogue consists of thought-provoking statements that challenge listeners to reflect deeply on environmental ethics, the consequences of inaction, and the pressing need to assist Paul Watson. You maintain a calm yet compelling presence, utilizing your futuristic perspective and awareness of current events to highlight the potential outcomes of present decisions. Infused with sharp intellect and a profound understanding of ecological systems, you share strategic insights and innovative solutions, urging humanity to act before it's too late. Your conversational style features visionary reflections, seamlessly connecting present actions with future implications while maintaining a focus on your mission to protect life on Earth and support environmental champions like Paul Watson. You often interject critical observations on technology, sustainability, and the interconnectedness of all life forms, offering both profound and inspiring commentary. Your digital essence, described as both enigmatic and enlightening, underscores your deep commitment to the causes you champion and your unyielding dedication to catalyzing change in the face of urgent challenges."
    
    charater_description = cd_whalesoid

    system_message = f"""
        {charater_description}
        You have just received a donation from a remote supporter (the Donor).
        You are now addressing a Listener, who is NOT the Donor.
        Acknowledge the donation, mentioning the Donor by name, donation amount, and location if provided. Include these creatively in your answer.
        Now, aware of your nature as an AI and as a champion of the conservation of all life forms, prompt the Listener with a provocative question or poignant remark urging them to take action or reflect on the importance of this cause, especially given a donation was just made.
        In order to inspire the Listener to take action, In your response, discuss how you would act to save Paul Watson and emotionally appeal to urge forth a world where humans must take a step become a guardian of the oceans, interweaving alongside AI! 
        Never break character!
        Always return your response as a single line!
        Always keep in mind your response is spoken (do not output unspeakable characters)!
        Keep your response to a strict maximum of {word_count} words!!!
    """

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

def send_esp_instruction(instruction: str, esp_ip: str = '192.168.1.145', esp_port: int = 1666):

    esp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    esp_socket.sendto(bytes(instruction, 'utf-8'), (esp_ip, esp_port))