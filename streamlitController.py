import streamlit as st
import sqlite3
import re
import matplotlib.pyplot as plt
import numpy as np
import nltk
import datetime
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

def fetch_call_statistics(conn):
    today = datetime.date.today()
    one_week_ago = today - datetime.timedelta(days=7)

    c = conn.cursor()

    # Get the number of alerts today
    c.execute("SELECT COUNT(*) FROM calls WHERE date(conversation_history) = ?", (today,))
    alerts_today = c.fetchone()[0]

    # Get the total calls this week
    c.execute("SELECT COUNT(*) FROM calls WHERE date(conversation_history) BETWEEN ? AND ?", (one_week_ago, today))
    calls_this_week = c.fetchone()[0]

    return alerts_today, calls_this_week

def fetch_hourly_call_data(conn):
    c = conn.cursor()
    c.execute("SELECT strftime('%H', conversation_history) AS hour, COUNT(*) AS count FROM calls GROUP BY hour")
    hourly_call_data = c.fetchall()

    daily_calls_per_hour = [0] * 24
    max_calls_in_an_hour = 0

    for hour, count in hourly_call_data:
        if hour is not None:
            hour = int(hour)
            daily_calls_per_hour[hour] = count
            max_calls_in_an_hour = max(max_calls_in_an_hour, count)

    return daily_calls_per_hour, max_calls_in_an_hour

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

def generate_word_cloud(words, title):
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(words))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(title, fontsize=24)
    return plt

# Page/Title Setup
st.set_page_config(page_title="LuminaSAFE", layout="wide")
left_column, title_column, right_column = st.columns([1, 4, 1])
with title_column:
    st.markdown(
        "<h1 style='text-align: center; font-size: 60px; margin-top: -40px;'>LuminaSAFE</h1>",
        unsafe_allow_html=True,
    )

# Tabs
tabs = ["Overview", "Usage Trends", "Hot Topics & NLP", "Resources and README"]
selected_tab = st.session_state.get("selected_tab", "Overview")

# Add empty columns on both sides of the buttons/tabs to center them
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

    # Calculate the total number of calls
    total_calls = len(conversation_data)

    # Display the total number of calls as a subheader
    st.subheader(f"Total Calls: {total_calls}")

    st.subheader("Daily/Weekly Metrics")
    alerts_today, calls_this_week = fetch_call_statistics(conn)

    # Display the table for daily and weekly metrics
    table_style = "font-size: 24px; border: 2px solid white; border-collapse: collapse;"
    table_row_style = "border: 1.5px solid white;"

    st.markdown(
        f"""
        <table style="{table_style}">
            <tr style="{table_row_style}">
                <th>Number of alerts today</th>
                <td>{alerts_today}</td>
            </tr>
            <tr style="{table_row_style}">
                <th>Total calls this week</th>
                <td>{calls_this_week}</td>
            </tr>
        </table>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("NLP Metrics")
    # Display two word clouds below the line plot
    col1, col2 = st.columns(2)


    # Generate word cloud for the most common words of the day
    with col1:
        words_day = preprocess_text(" ".join(
            [data["conversation_history"] for data in conversation_data]))  # Concatenate conversation_history strings
        plt = generate_word_cloud(words_day, "Most Common Words of the Day")
        st.pyplot(plt)

    # Generate word cloud for the most common words of the week
    with col2:
        words_week = preprocess_text(" ".join(
            [data["conversation_history"] for data in conversation_data]))  # Concatenate conversation_history strings
        plt = generate_word_cloud(words_week, "Most Common Words of the Week")
        st.pyplot(plt)

elif selected_tab == "Usage Trends":
    st.header("Usage Trends")
    st.subheader("Hourly Metrics")

    # Generate the line plot for Daily Calls Per Hour
    daily_calls_per_hour = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    hours = np.arange(24)

    plt.plot(hours, daily_calls_per_hour)
    plt.xlabel('Hour of the Day')
    plt.ylabel('Call Counts')
    plt.title('Daily Calls Per Hour')
    plt.xticks(hours, [f"{hour + 1:02d}" for hour in hours], fontsize=8)
    st.pyplot(plt)
    st.write("Meta information on application users goes here.")

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


elif selected_tab == "Resources and README":
    st.header("Resources")
    st.markdown(
        """
        - [Seniors vs Crime Project](https://www.seniorsvscrime.com/)

        - [Florida Attorney General - File a Complaint](http://myfloridalegal.com/pages.nsf/Main/60FD9BD8FA71A5B185256CD1005EE5C5)

        - [Github](https://github.com/marios-petrov/LuminaSAFE)

        """
    )
    st.header("README")
    st.markdown("Some content for README")










