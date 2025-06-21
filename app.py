# from elevenlabs import (
#     AgentConfig,
#     ConversationSimulationSpecification,
#     ElevenLabs,
# )

# client  = ElevenLabs(api_key="")

# response = client.conversational_ai.agents.simulate_conversation(
#     agent_id="",
#     simulation_specification=ConversationSimulationSpecification(
#         simulated_user_config=AgentConfig(
#             first_message="Hello, how can I help you today?",
#             language="en",
#         ),
#     ),
# )

# print(response)

import json
from datetime import datetime
from elevenlabs import (
    AgentConfig,
    ConversationSimulationSpecification,
    ElevenLabs,
    VoiceSettings,
    play,
)

# 🌐 Agent IDs for different languages
AGENT_IDS = {
    "en": "",
    "hi": ""
}

#Load user data
def load_user_data(user_id, path="user_data.json"):
    with open(path, "r") as f:
        data = json.load(f)
    return data.get(user_id, None)

def generate_prompt(user):
    greeting = "Hi" if user["language"] == "en" else "नमस्ते"
    return f"""
    You are a meditation assistant named "MindfulMate". Your tasks:
    1. Remind the user to meditate.
    2. Answer questions about mindfulness.
    3. Celebrate their progress.

    User Info:
    - Name: {user['name']}
    - Last Session: {user['last_session']}
    - Sessions Attended: {user['sessions_attended']}
    - Streak: {user['streak']} days
    - Goal: {user['goal']}

    Start with: "{greeting} {user['name']}! Ready for a quick meditation session?"
    """

# 🔁 Run meditation flow
def start_meditation_bot(user_id):
    user = load_user_data(user_id)
    if not user:
        print(f"❌ User '{user_id}' not found.")
        return

    lang = user.get("language", "en")
    agent_id = AGENT_IDS.get(lang)
    if not agent_id:
        print(f"❌ No agent available for language: {lang}")
        return

    prompt = generate_prompt(user)

    client = ElevenLabs(api_key="")

    response = client.conversational_ai.agents.simulate_conversation(
        agent_id=agent_id,
        simulation_specification=ConversationSimulationSpecification(
            simulated_user_config=AgentConfig(
                first_message="hello" if lang == "en" else "नमस्ते",
                language=lang,
                prompt={
                    "prompt": prompt,
                    "llm": "gemini-2.0-flash-lite",  
                    "temperature": 0.5
                }
            )
        )
    )
    print(response)


if __name__ == "__main__":
    start_meditation_bot("user_123")  