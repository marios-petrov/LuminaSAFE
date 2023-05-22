from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from gptController import call_chatgpt_api, summarize_text, get_text_embedding
from databaseController import create_connection, create_table, update_or_insert_call
from datetime import datetime
from apiKeys import TWILIO_PHONE_NUMBER, TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID

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
    from_number = request.values.get('From', None)
    conversation_history = conversations.get(from_number, "")

    if not conversation_history:
        response = VoiceResponse()
        gather = Gather(input='speech', action='/process_speech', hints='yes, no, maybe')
        gather.say("Hi I'm Lumina, How can I help you today?")
        response.append(gather)
    else:
        response = VoiceResponse()
        gather = Gather(input='speech', action='/process_speech', hints='yes, no, maybe')
        response.append(gather)

    response.redirect('/answer')

    return Response(str(response), content_type='text/xml')



@app.route('/sms', methods=['POST'])
def sms_process():
    body = request.values.get('Body', None)
    from_number = request.values.get('From', None)

    if body and from_number:
        conversation_history = conversations.get(from_number, "")

        total_tokens = len(conversation_history) + len(body)
        if total_tokens > TOKEN_LIMIT:
            # Summarize to shorten
            conversation_history = summarize_text(conversation_history)

        chatgpt_response = call_chatgpt_api(body, conversation_history)

        updated_conversation_history = f"{conversation_history}\nUser: {body}\nAI: {chatgpt_response}"
        conversations[from_number] = updated_conversation_history

        conversation_vector = get_text_embedding(updated_conversation_history)

        update_or_insert_call(connection, from_number, datetime.utcnow(), updated_conversation_history, conversation_vector.tobytes(), "sms")

        twilio_client.messages.create(
            body=chatgpt_response,
            from_=TWILIO_PHONE_NUMBER,
            to=from_number)

    return Response(status=200)


@app.route('/process_speech', methods=['POST'])
def process_speech():
    response = VoiceResponse()
    user_speech = request.values.get('SpeechResult', None)
    from_number = request.values.get('From', None)

    if user_speech and from_number:
        with create_connection("phone_calls.db") as connection:
            conversation_history = conversations.get(from_number, "")

            total_tokens = len(conversation_history) + len(user_speech)
            if total_tokens > TOKEN_LIMIT:
                conversation_history = summarize_text(conversation_history)

            chatgpt_response = call_chatgpt_api(user_speech, conversations.get(from_number, ""))

            updated_conversation_history = f"{conversation_history}\nUser: {user_speech}\nAI: {chatgpt_response}"
            conversations[from_number] = updated_conversation_history

            conversation_vector = get_text_embedding(updated_conversation_history)

            current_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            update_or_insert_call(connection, from_number, current_timestamp, updated_conversation_history,
                                  conversation_vector.tobytes(), 'call')

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
