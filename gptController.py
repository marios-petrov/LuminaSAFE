from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer
import openai

# Set your OpenAI API key
openai.api_key = "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"

# Load the T5 model for summarization
t5_tokenizer = T5Tokenizer.from_pretrained('t5-small')
t5_model = T5ForConditionalGeneration.from_pretrained('t5-small')

# Load the SBERT model
sbert_model = SentenceTransformer('paraphrase-distilroberta-base-v1')

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