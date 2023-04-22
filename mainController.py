from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from gptController import call_chatgpt_api, summarize_text, get_text_embedding
from databaseController import create_connection, create_table, update_or_insert_call

# Set your Twilio API credentials and phone number
TWILIO_ACCOUNT_SID = "AC66723cf4a1d3e771fa1ed1419f3cd4a3"
TWILIO_AUTH_TOKEN = "508fe477e35249cd1b4c5321b51f1ec1"
TWILIO_PHONE_NUMBER = "+1-844-779-2582"

# Initialize the Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize the database and create the calls table
connection = create_connection("phone_calls.db")
if connection is not None:
    create_table(connection)

# Set the token limit for your specific GPT model (e.g., text-davinci-002 has a 4096 token limit)
TOKEN_LIMIT = 4096

conversations = {}

app = Flask(__name__)

@app.route('/answer', methods=['POST'])
def answer_call():
    response = VoiceResponse()

    gather = Gather(input='speech', action='/process_speech', hints='yes, no, maybe')
    gather.say("Please speak your message.")
    response.append(gather)

    response.redirect('/answer')

    return Response(str(response), content_type='text/xml')

@app.route('/process_speech', methods=['POST'])
def process_speech():
    response = VoiceResponse()
    user_speech = request.values.get('SpeechResult', None)
    from_number = request.values.get('From', None)

    if user_speech and from_number:
        conversation_history = conversations.get(from_number, "")

        # Check if the conversation_history plus the new user input exceed the token limit
        total_tokens = len(conversation_history) + len(user_speech)
        if total_tokens > TOKEN_LIMIT:
            # Summarize the conversation history if it's too long
            conversation_history = summarize_text(conversation_history)

        chatgpt_response = call_chatgpt_api(user_speech, conversations.get(from_number, ""))

        # Update the conversation history for the user
        updated_conversation_history = f"{conversation_history}\nUser: {user_speech}\nAI: {chatgpt_response}"
        conversations[from_number] = updated_conversation_history

        # Get the text embedding of the conversation history
        conversation_vector = get_text_embedding(updated_conversation_history)

        # Update the call data in the database
        update_or_insert_call(connection, from_number, updated_conversation_history, conversation_vector.tobytes())

        response.say(chatgpt_response)
        response.redirect('/answer')
    else:
        response.say("I couldn't understand your input, please try again.")
        response.redirect('/answer')

    return Response(str(response), content_type='text/xml')

@app.route('/', methods=['GET', 'POST'])
def index():
    return "Flask app is running"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)