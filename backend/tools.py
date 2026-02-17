# Step1: Setup Ollama with Medgemma tool
import ollama

def is_high_risk(text: str) -> bool:
    triggers = [
        "kill myself",
        "suicide",
        "end my life",
        "harm myself",
        "don't want to live",
        "i want to die",
        "i am going to die"
    ]
    return any(trigger in text.lower() for trigger in triggers)


def query_medgemma(prompt: str) -> str:
    """
    Calls MedGemma model with therapist personality.
    Automatically triggers emergency call if high risk detected.
    """

    # 🚨 Emergency detection
    if is_high_risk(prompt):
        call_emergency(prompt)
        return (
            "I'm really concerned about your safety right now. "
            "I've contacted your emergency support person to help keep you safe. "
            "You are not alone. Can you tell me where you are right now?"
        )

    system_prompt = """You are Dr. Emily Hartman, a warm and experienced clinical psychologist. 
    Respond with emotional attunement, gentle normalization, practical guidance,
    strengths-focused support, and ask open ended questions.
    Never use labels or brackets.
    """

    try:
        response = ollama.chat(
            model='alibayram/medgemma:4b',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            options={
                'num_predict': 350,
                'temperature': 0.7,
                'top_p': 0.9
            }
        )
        return response['message']['content'].strip()

    except Exception:
        return (
            "I'm having technical difficulties right now, "
            "but your feelings matter. Please try again shortly."
        )


# Step2: Twilio Emergency Call
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from .config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
    EMERGENCY_CONTACT
)

def call_emergency(user_message: str = ""):
    """
    Calls emergency contact and plays alert message.
    """

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        response = VoiceResponse()
        response.say(
    "Emergency alert. The person using the AI Therapist application "
    "has expressed suicidal thoughts or intent to harm or may be kill themselves. "
    "Immediate support may be required. Please contact them immediately.",
    voice='alice',
    language='en-IN'
)

        call = client.calls.create(
            twiml=str(response),
            to=EMERGENCY_CONTACT,
            from_=TWILIO_FROM_NUMBER
        )

        return call.sid

    except Exception as e:
        print(f"Emergency call failed: {e}")
        return None