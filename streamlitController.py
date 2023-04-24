import streamlit as st
import sqlite3
import re
import matplotlib.pyplot as plt
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
from wordcloud import WordCloud

# Connecting to the database
def fetch_conversation_data(conn):
    conversation_data = []

    try:
        c = conn.cursor()
        c.execute("SELECT id, phone_number, conversation_history FROM calls")

        rows = c.fetchall()
        for row in rows:
            conversation_data.append({"id": row[0], "phone_number": row[1], "conversation_history": row[2]})

    except sqlite3.Error as e:
        print(e)

    return conversation_data

DATABASE_NAME = "phone_calls.db"
conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
conversation_data = fetch_conversation_data(conn)

def preprocess_text(text):
    # Lowercase the text
    text = text.lower()

    # Tokenize words
    words = word_tokenize(text)

    # Remove punctuation
    words = [word for word in words if word.isalnum()]

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    stop_words.update(["user", "jupiter"])  # Add "user" and "jupiter" to the list of stopwords
    words = [word for word in words if word not in stop_words]

    return words

def count_phone_numbers(conversation_history):
    phone_number_pattern = r"\d{3}-\d{3}-\d{4}"
    phone_numbers = re.findall(phone_number_pattern, conversation_history)

    phone_number_counts = {}
    for phone_number in phone_numbers:
        if phone_number not in phone_number_counts:
            phone_number_counts[phone_number] = 1
        else:
            phone_number_counts[phone_number] += 1

    return phone_number_counts

def plot_phone_number_counts(phone_number_counts):
    phone_numbers = list(phone_number_counts.keys())
    counts = list(phone_number_counts.values())

    index = np.arange(len(phone_numbers))
    plt.figure(figsize=(6, 4))
    plt.bar(index, counts)
    plt.xlabel('Phone Numbers', fontsize=12)
    plt.ylabel('Counts', fontsize=12)
    plt.xticks(index, phone_numbers, fontsize=10, rotation=30)
    return plt

def plot_word_frequency(words, top_n=10):
    word_freq = Counter(words)
    common_words = word_freq.most_common(top_n)

    words, frequencies = zip(*common_words)
    index = np.arange(len(words))
    plt.figure(figsize=(5.8, 4))
    plt.bar(index, frequencies)
    plt.xlabel('Words', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.xticks(index, words, fontsize=10, rotation=30)
    return plt



# Page/Title Setup
st.set_page_config(page_title="LuminaSAFE", layout="wide")
left_column, title_column, right_column = st.columns([1, 4, 1])
with title_column:
    st.markdown(
        "<h1 style='text-align: center; font-size: 60px; margin-top: -40px;'>LuminaSAFE</h1>",
        unsafe_allow_html=True,
    )

# Create custom tabs using bigger buttons in a single row
tabs = ["Overview", "Alerts", "Usage Trends", "Resources", "Hot Topics & NLP"]
selected_tab = st.session_state.get("selected_tab", "Overview")

# Add empty columns on both sides of the buttons to center them
left_space, *columns, right_space = st.columns([1] + [2]*len(tabs) + [1])
button_style = "style='width: 100%; height: 50px; margin-bottom: 10px;'"

for i, tab in enumerate(tabs):
    with columns[i]:
        if st.button(tab, key=f"tab_button_{i}"):
            selected_tab = tab
            st.session_state.selected_tab = selected_tab

st.write("\n")

# Display content based on the selected tab
if selected_tab == "Overview":
    st.header("Overview")
    dropdown_options = ["Technical Overview", "Scientific Overview"]
    selected_option = st.selectbox("Select an option:", dropdown_options)

    if selected_option == "Technical Overview":
        st.write("Technical Overview content goes here.")
    elif selected_option == "Scientific Overview":
        st.write("Scientific Overview content goes here.")

elif selected_tab == "Alerts":
    st.header("Alerts")
    st.write("Metrics and alerts related to the dataset go here.")

elif selected_tab == "Usage Trends":
    st.header("Usage Trends")
    st.write("Meta information on application users goes here.")

elif selected_tab == "Resources":
    st.header("Resources")
    st.markdown(
        """
        - [Seniors vs Crime Project](https://www.seniorsvscrime.com/)
        - [Florida Attorney General - File a Complaint](http://myfloridalegal.com/pages.nsf/Main/60FD9BD8FA71A5B185256CD1005EE5C5)
        """
    )

elif selected_tab == "Hot Topics & NLP":
    st.header("Hot Topics & NLP")

    # Display a list of phone numbers with associated conversation histories
    phone_numbers = [data["phone_number"] for data in conversation_data]
    selected_phone_number = st.selectbox("Select a phone number:", phone_numbers)

    # Find the corresponding conversation history for the selected phone number
    selected_conversation_history = None
    for data in conversation_data:
        if data["phone_number"] == selected_phone_number:
            selected_conversation_history = data["conversation_history"]
            break

    # Display the conversation history and perform NLP analysis
    if selected_conversation_history:
        st.subheader("Conversation History")
        formatted_conversation = selected_conversation_history.replace("User:", "\nUser:").replace("AI:", "\nAI:")
        st.write(formatted_conversation)

        # Create two columns to display the plots side by side
        col1, col2 = st.columns(2)

        # Perform NLP analysis on the conversation history
        phone_number_counts = count_phone_numbers(selected_conversation_history)

        with col1:
            # Add the title using st.markdown() with custom HTML
            st.markdown(
                "<h4 style='font-size: 24px; font-family: sans-serif; color: #ffffff;'>Phone Numbers Mentioned in the Conversation</h4>",
                unsafe_allow_html=True)
            plt = plot_phone_number_counts(phone_number_counts)
            st.pyplot(plt)

        with col2:
            # Add the title using st.markdown() with custom HTML
            top_n = 10
            st.markdown(
                f"<h4 style='font-size: 24px; font-family: sans-serif; color: #ffffff;'>Top {top_n} Most Frequent Words in the Conversation</h4>",
                unsafe_allow_html=True)
            words = preprocess_text(selected_conversation_history)
            plt = plot_word_frequency(words)
            st.pyplot(plt)












