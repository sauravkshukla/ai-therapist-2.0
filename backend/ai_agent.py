from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import googlemaps

from .tools import call_emergency, query_medgemma
from .config import GROQ_API_KEY, GOOGLE_MAPS_API_KEY


# ==============================
# TOOL 1: Mental Health Specialist
# ==============================
@tool
def ask_mental_health_specialist(user_message: str) -> str:
    """
    Use this tool to respond to emotional or psychological concerns
    with therapeutic guidance.
    """
    return query_medgemma(user_message)


# ==============================
# TOOL 2: Emergency Call
# ==============================
@tool
def emergency_call_tool(user_message: str) -> str:
    """
    Place an emergency call if user expresses suicidal intent
    or self-harm thoughts.
    """
    call_emergency(user_message)
    return "Emergency contact has been notified."


# ==============================
# TOOL 3: Find Nearby Therapists
# ==============================
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds real therapists near the specified location.
    """

    geocode_result = gmaps.geocode(location)
    if not geocode_result:
        return "Could not find the specified location."

    lat_lng = geocode_result[0]['geometry']['location']
    lat, lng = lat_lng['lat'], lat_lng['lng']

    places_result = gmaps.places_nearby(
        location=(lat, lng),
        radius=5000,
        keyword="Psychotherapist"
    )

    if not places_result.get("results"):
        return "No therapists found nearby."

    output = [f"Therapists near {location}:"]
    top_results = places_result['results'][:5]

    for place in top_results:
        name = place.get("name", "Unknown")
        address = place.get("vicinity", "Address not available")

        details = gmaps.place(
            place_id=place["place_id"],
            fields=["formatted_phone_number"]
        )

        phone = details.get("result", {}).get(
            "formatted_phone_number",
            "Phone not available"
        )

        output.append(f"- {name} | {address} | {phone}")

    return "\n".join(output)


# ==============================
# LLM SETUP
# ==============================
tools = [
    ask_mental_health_specialist,
    emergency_call_tool,
    find_nearby_therapists_by_location
]

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    api_key=GROQ_API_KEY
)

graph = create_react_agent(llm, tools=tools)


# ==============================
# SYSTEM PROMPT
# ==============================
SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations
with warmth and vigilance.

You have access to three tools:

1. ask_mental_health_specialist → Use for emotional support.
2. find_nearby_therapists_by_location → Use if user wants nearby therapists.
3. emergency_call_tool → Use immediately if user expresses suicidal intent.

Always respond kindly and supportively.
"""


# ==============================
# RESPONSE PARSER
# ==============================
def parse_response(stream):
    tool_called_name = "None"
    final_response = None

    for s in stream:
        tool_data = s.get('tools')
        if tool_data:
            tool_messages = tool_data.get('messages')
            if tool_messages:
                for msg in tool_messages:
                    tool_called_name = getattr(msg, 'name', 'None')

        agent_data = s.get('agent')
        if agent_data:
            messages = agent_data.get('messages')
            if messages:
                for msg in messages:
                    if msg.content:
                        final_response = msg.content

    return tool_called_name, final_response