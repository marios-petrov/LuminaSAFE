import streamlit as st
import sqlite3
import re
import matplotlib.pyplot as plt
import numpy as np
import datetime
import random
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
from wordcloud import WordCloud

DATABASE_NAME = "phone_calls.db"
conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)

area_codes = [
    "201", "202", "203", "205", "206", "207", "208", "209", "210", "212",
    "213", "214", "215", "216", "217", "218", "219", "224", "225", "228",
    "229", "231", "234", "239", "240", "248", "251", "252", "253", "254",
    "256", "260", "262", "267", "269", "270", "272", "276", "281", "301",
    "302", "303", "304", "305", "307", "308", "309", "310", "312", "313",
    "314", "315", "316", "317", "318", "319", "320", "321", "323", "325",
    "330", "331", "334", "336", "337", "339", "346", "347", "351", "352",
    "360", "361", "385", "386", "401", "402", "404", "405", "406", "407",
    "408", "409", "410", "412", "413", "414", "415", "417", "419", "423",
    "424", "425", "430", "432", "434", "435", "440", "442", "443", "469",
    "470", "475", "478", "479", "480", "484", "501", "502", "503", "504",
    "505", "507", "508", "509", "510", "512", "513", "515", "516", "517",
    "518", "520", "530", "531", "534", "539", "540", "541", "551", "559",
    "561", "562", "563", "567", "570", "571", "573", "574", "575", "580",
    "585", "586", "601", "602", "603", "605", "606", "607", "608", "609",
    "610", "612", "614", "615", "616", "617", "618", "619", "620", "623",
    "626", "628", "629", "630", "631", "636", "641", "646", "650", "651",
    "660", "661", "662", "667", "669", "678", "681", "682", "684", "701",
    "702", "703", "704", "706", "707", "708", "712", "713", "714", "715",
    "716", "717", "718", "719", "720", "724", "727", "731", "732", "734",
    "737", "740", "747", "754", "757", "760", "762", "763", "765", "769",
    "770", "772", "773", "774", "775", "779", "781", "785", "786", "801",
    "802", "803", "804", "805", "806", "808", "810", "812", "813", "814",
    "815", "816", "817", "818", "828", "830", "831", "832", "843", "845",
    "847", "848", "850", "856", "857", "858", "859", "860", "862", "863",
    "864", "865", "870", "872", "878", "901", "903", "904", "906", "907",
    "908", "909", "910", "912", "913", "914", "915", "916", "917", "918",
    "919", "920", "925", "928", "931", "936", "937", "938", "940", "941",
    "947", "949", "951", "952", "954", "956", "959", "970", "971", "972",
    "973", "978", "979", "980", "984", "985", "989"
]

# Connecting to the database
def fetch_conversation_data(conn):
    conversation_data = []

    try:
        c = conn.cursor()
        c.execute("SELECT DISTINCT phone_number FROM calls")

        phone_numbers = c.fetchall()
        for phone_number in phone_numbers:
            c.execute("SELECT conversation_history FROM calls WHERE phone_number = ? ORDER BY timestamp DESC LIMIT 1", phone_number)
            conversation_history = c.fetchone()[0]
            conversation_data.append({"phone_number": phone_number[0], "conversation_history": conversation_history})

    except sqlite3.Error as e:
        print(e)

    return conversation_data


conversation_data = fetch_conversation_data(conn)

def fetch_call_statistics(conn):
    today = datetime.date.today()
    one_week_ago = today - datetime.timedelta(days=7)

    # Convert dates to strings in the format 'YYYY-MM-DD'
    today_str = today.strftime('%Y-%m-%d')
    one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')

    c = conn.cursor()

    # Get the number of alerts today
    c.execute("SELECT COUNT(*) FROM calls WHERE date(timestamp) = ?", (today_str,))
    alerts_today = c.fetchone()[0]

    # Get the total calls this week
    c.execute("SELECT COUNT(DISTINCT phone_number) FROM calls WHERE date(timestamp) BETWEEN ? AND ?", (one_week_ago_str, today_str))
    calls_this_week = c.fetchone()[0]

    return alerts_today, calls_this_week


def fetch_hourly_call_data(conn):
    c = conn.cursor()
    c.execute("SELECT strftime('%H', timestamp) AS hour, COUNT(*) AS count FROM calls GROUP BY hour")
    hourly_call_data = c.fetchall()

    daily_calls_per_hour = [0] * 24
    max_calls_in_an_hour = 0

    for hour, count in hourly_call_data:
        if hour is not None:
            hour = int(hour)
            daily_calls_per_hour[hour] = count
            max_calls_in_an_hour = max(max_calls_in_an_hour, count)

    return daily_calls_per_hour, max_calls_in_an_hour

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

def decode_if_bytes(text):
    # If text is a bytes object, decode it to a string
    if isinstance(text, bytes):
        return text.decode('utf-8')  # or use 'latin-1' or 'iso-8859-1' if 'utf-8' doesn't work
    return text

def generate_word_cloud(words, title):
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(words))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(title, fontsize=24)
    return plt

# Page/Title Setup
st.set_page_config(page_title="LuminaSAFE", layout="wide")
st.title("LuminaSAFE")

# Display content based on the selected button
selected_button = st.sidebar.radio("Navigation", ["Overview", "Usage Trends", "Hot Topics & NLP", "Resources and README"])

# Overview page
if selected_button == "Overview":
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

# Usage Trends page
elif selected_button == "Usage Trends":
    st.header("Usage Trends")

    # Create synthetic data for the hourly metric
    hours = np.arange(24)
    hourly_data = [random.randint(50, 200) + random.randint(-50, 50) for _ in hours]

    # Create two columns to display the figures side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hourly Metrics")

        plt.figure(figsize=(7, 5))  # Adjust the figure size as desired
        plt.plot(hours, hourly_data)
        plt.xlabel('Hour of the Day')
        plt.ylabel('Call Counts')
        plt.title('Dynamic Hourly Metrics')
        plt.xticks(hours, [f"{hour + 1:02d}" for hour in hours], fontsize=8)
        st.pyplot(plt)

    with col2:
        st.subheader("Caller/Texter Origin Heatmap")

        m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)  # Centered around the United States

        # Generate synthetic data or use a larger dataset to populate the heatmap across the country
        heatmap_data = []
        num_points = 24  # Adjust the number of points as desired

        for _ in range(num_points):
            lat = np.random.uniform(24, 50)  # Latitude range across the continental United States
            lon = np.random.uniform(-125, -66)  # Longitude range across the continental United States
            weight = np.random.randint(1, 10)  # Adjust weight as desired
            heatmap_data.append([lat, lon, weight])

        # Add the heatmap layer to the map
        HeatMap(heatmap_data, radius=10).add_to(m)  # Adjust radius as desired for smaller points

        # Display the map in Streamlit
        folium_static(m, width=700, height=515)  # Adjust width and height as desired

# Hot Topics & NLP page
elif selected_button == "Hot Topics & NLP":
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

# Resources and README page
elif selected_button == "Resources and README":
    st.header("Resources")
    st.markdown(
        """
        - [Seniors vs Crime Project](https://www.seniorsvscrime.com/)

        - [Florida Attorney General - File a Complaint](http://myfloridalegal.com/pages.nsf/Main/60FD9BD8FA71A5B185256CD1005EE5C5)

        - [Github] 

        """
    )
    st.header("README")
    st.markdown("Some content for README")










