from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer
from sqlite3 import Error
import sqlite3
import openai

# Set your Twilio API credentials and phone number
TWILIO_ACCOUNT_SID = "AC66723cf4a1d3e771fa1ed1419f3cd4a3"
TWILIO_AUTH_TOKEN = "508fe477e35249cd1b4c5321b51f1ec1"
TWILIO_PHONE_NUMBER = "+1-844-779-2582"

# Set your OpenAI API key
openai.api_key = "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"

# Initialize the Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Set the token limit for your specific GPT model (e.g., text-davinci-002 has a 4096 token limit)
TOKEN_LIMIT = 4096

# Database setup
DATABASE_NAME = "phone_calls.db"

# Load the T5 model for summarization
t5_tokenizer = T5Tokenizer.from_pretrained('t5-small')
t5_model = T5ForConditionalGeneration.from_pretrained('t5-small')

# Load the SBERT model
sbert_model = SentenceTransformer('paraphrase-distilroberta-base-v1')

app = Flask(__name__)

conversations = {}

def call_chatgpt_api(text, conversation_history):
    model_engine = "text-davinci-002"
    prompt = f"{conversation_history}\nUser: {text}\nAI:"

    try:
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5
        )

        response_text = response.choices[0].text.strip()
        return response_text

    except Exception as e:
        print("Error calling ChatGPT API:", e)
        return None


def summarize_text(text):
    # Prepare the input for the T5 model
    input_ids = t5_tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)

    # Generate the summary
    summary_ids = t5_model.generate(input_ids, num_return_sequences=1, max_length=150, early_stopping=True)

    # Decode the summary
    summary = t5_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary

def get_text_embedding(text):
    embeddings = sbert_model.encode([text])
    return embeddings

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    create_table_sql = """CREATE TABLE IF NOT EXISTS calls (
                            id INTEGER PRIMARY KEY,
                            phone_number TEXT NOT NULL,
                            conversation_history TEXT,
                            conversation_vector BLOB
                        );"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_call(conn, phone_number, conversation_history, conversation_vector):
    sql = """INSERT INTO calls(phone_number, conversation_history, conversation_vector) VALUES(?, ?, ?);"""
    cur = conn.cursor()
    cur.execute(sql, (phone_number, conversation_history, conversation_vector))
    conn.commit()
    return cur.lastrowid

# Initialize the database and create the calls table
connection = create_connection(DATABASE_NAME)
if connection is not None:
    create_table(connection)

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

        chatgpt_response = call_chatgpt_api(user_speech, conversation_history)

        # Update the conversation history for the user
        conversations[from_number] = f"{conversation_history}\nUser: {user_speech}\nAI: {chatgpt_response}"

        # Get the text embedding of the conversation history
        conversation_vector = get_text_embedding(conversations[from_number])

        # Insert the call data into the database
        call_id = insert_call(connection, from_number, conversations[from_number], conversation_vector.tobytes())

        response.say(chatgpt_response)
        response.redirect('/answer')
    else:
        response.say("I couldn't understand your input, please try again.")
        response.redirect('/answer')

    return Response(str(response), content_type='text/xml')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

