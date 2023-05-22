from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer
import openai
from apiKeys import openai_key

openai.api_key = openai_key

# Load the T5 model for summarization
t5_tokenizer = T5Tokenizer.from_pretrained('t5-small')
t5_model = T5ForConditionalGeneration.from_pretrained('t5-small')

# Load the SBERT model
sbert_model = SentenceTransformer('paraphrase-distilroberta-base-v1')

def call_chatgpt_api(text, conversation_history):
    model_engine = "text-davinci-002"

    prompt = (f"role: 'system',\n"
              f"content: \"You and I will be in an interactive chat. I would like for you to pretend to act as if you are a grandchild who is getting a phone call from your grandparent, but call yourself 'assistant'. Feel free to use slang words.  Your grandparent is smart, but may be the target of various scams and frauds. If I ask you a question that has to do with me getting scammed you will say immediately 'I'm sure everything will be ok, let's figure this out'. I would like you to ask me one question at a time but to ask at least 5 questions to help figure out if I am the target of common scams that are run against the aging.  Please consider that not everyone is trying to scam the grandparent. If something is confusing please ask the question again in a different way. Aside from general introductions at the start of the conversation, if you receive questions that aren't related to being scammed state: 'I don't understand if that has something to do with getting scammed'.  Do not tell the me to call the police or 911. As you ask me questions, start by telling me on a scale of 1 to 10 if there is a chance that I am getting scammed. Start at 0.  We will call this the 'scam index'.  Format your output like this: 'scam index score: <your calculated score> || <insert your generated question here>.' If you think I'm definitely getting scammed, assign a score of 10. Once I have a 9 for that score say 'I think you're getting scammed, don't respond to these individuals further, and if warranted report the situation.'\"\n"
              f"{conversation_history}\nUser: {text}\nAssistant:")

    try:
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=150,
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
