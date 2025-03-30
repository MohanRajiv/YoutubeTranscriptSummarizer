import streamlit as st
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import os
import google.generativeai as genai
import requests
import re

# Load environment variables
load_dotenv() 
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the search_keyword_print_startimes function
def search_keyword_print_startimes(transcript, search_word):
    data = [t['text'] for t in transcript]
    
    # Removing non-alphanumeric characters
    data = [re.sub(r"[^a-zA-Z0-9 ]", "", line) for line in data]
    
    time = []
    lines = []
    for i, line in enumerate(data):
        if search_word in line:
            start_time = transcript[i]['start']
            time.append(start_time)
            lines.append(line)
    
    return time, lines

# Define the extract_transcript_details function
def extract_transcript_details(youtube_video_url, start_time=None, end_time=None):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Get the total duration of the video
        total_duration = transcript_text[-1]['start'] + transcript_text[-1]['duration']

        if start_time is None and end_time is None:
            # Summarize the entire video
            transcript = ""
            for i in transcript_text:
                transcript += " " + i["text"]
            return transcript
        else:
            # Check if the entered timestamps are within the bounds of the video duration
            if start_time < 0 or end_time < start_time or end_time > total_duration:
                st.error("Invalid timestamps. Please enter valid start and end times.")
                return None

            # Extract transcript based on timestamps
            filtered_transcript = ""
            for i in transcript_text:
                if start_time <= i['start'] <= end_time:
                    filtered_transcript += " " + i["text"]
            return filtered_transcript

    except Exception as e:
        st.error("Error extracting transcript. Please check the YouTube video link.")
        raise e

# Define the generate_chapters function
def generate_chapters(transcript_text):
    try:
        # Calculate the total duration of the transcript text
        total_duration = sum([segment['duration'] for segment in transcript_text])
        chapters = {}
        chapter_start = 0
        chapter_end = 60  # Set the chapter length to 1 minute

        # Generate chapters based on 1-minute intervals
        while chapter_end <= total_duration:
            chapter_text = ""
            for segment in transcript_text:
                if segment['start'] >= chapter_start and segment['start'] <= chapter_end:
                    chapter_text += " " + segment['text']
                elif segment['start'] > chapter_end:
                    break

            chapters[f"Chapter {chapter_start}-{chapter_end}"] = chapter_text
            chapter_start = chapter_end
            chapter_end += 60
        
        return chapters
    except Exception as e:
        st.error("Error generating chapters.")
        raise e

# Define the generate_gemini_content function
def generate_gemini_content(transcript_text, prompt, max_words):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt + transcript_text)
    
    # Split the text into sentences using regular expressions
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', response.text)
    
    # Iterate through the sentences and collect them until the total word count reaches max_words
    word_count = 0
    summary_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if word_count + len(words) <= max_words:
            summary_sentences.append(sentence)
            word_count += len(words)
        else:
            break
    
    # Combine the summary sentences into a summary
    summary = ' '.join(summary_sentences)
    return summary

# Define the print_time function
def print_time(search_word, time, lines):
    st.write(f"'{search_word}' was mentioned at:")
    
    # Calculate the accurate time according to the video's duration
    data = [["Start Times", "Sentence Mentioned"]]  # Title row
    for t, l in zip(time, lines):
        hours = int(t // 3600)
        minutes = int(t // 60)
        seconds = int(t % 60)
        data.append([f"{hours:02d}:{minutes:02d}:{seconds:02d}", l])
        
        with open("Output.txt", "a") as text_file:
            print(f"{hours:02d}:{minutes:02d}:{seconds:02d}", file=text_file)
    
    st.table(data)

# Custom CSS for styling
st.markdown("""
<style>
body {
    color: white;
    background-color: black;
}
.stTextInput > div > div > input {
    color: black !important;
}
.stSelectbox {
    color: white;
}
.stSelectbox option {
    color: black;
}
</style>
""", unsafe_allow_html=True)

st.title("YouTube Search & Summarizer")
st.markdown("---")
youtube_link = st.text_input("Enter YouTube Video Link:", help="Paste the link to the YouTube video.")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

    # Sidebar options
    # Sidebar options
st.sidebar.title("Options")
mode = st.sidebar.radio("Select Mode", ("Whole Video", "Specific Timestamps", "Search Keyword"), help="Choose the mode of operation.")

# Declare max_words here for both modes
max_words = st.sidebar.number_input("Maximum Number of Words for Summary:", min_value=10, max_value=1000, value=250, help="Enter the maximum number of words for the summary.")

if mode == "Specific Timestamps":
    start_time_min = st.sidebar.number_input("Start Time (in minutes):", help="Enter the start time of the segment.")
    end_time_min = st.sidebar.number_input("End Time (in minutes):", help="Enter the end time of the segment.")
    
    # Convert minutes to seconds
    start_time = start_time_min * 60
    end_time = end_time_min * 60
elif mode == "Search Keyword":
    search_word = st.sidebar.text_input("Enter Keyword to Search in Transcript:", "")

if mode == "Search Keyword":
    with st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True):
        search_button = st.button("Search", key="search_button", help="Click to search for the keyword.")
        
        if search_button:
            if not search_word:
                st.error("Please enter a keyword to search.")
            else:
                transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
                start_times, lines = search_keyword_print_startimes(transcript_text, search_word)
                
                if start_times:
                    print_time(search_word, start_times, lines)
                else:
                    st.write(f"No occurrences of the keyword '{search_word}' found in the transcript.")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    with st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True):
        summarize_button = st.button("Summarize", key="summarize_button", help="Click to summarize the video.")
        
        if summarize_button:
            if mode == "Whole Video":
                transcript_text = extract_transcript_details(youtube_link)
            elif mode == "Specific Timestamps":
                transcript_text = extract_transcript_details(youtube_link, start_time, end_time)
            
            if transcript_text:
                default_prompt = """
                You are a YouTube video summarizer. You will be taking the transcript text and summarizing the video, providing the important points. No timestamps.
                Please provide the summary of the text given here. Make the formatting nice. Add spaces between points.
                """
                summary = generate_gemini_content(transcript_text, default_prompt, max_words)
                st.markdown("---")
                st.markdown("### Video Summary:")
                st.write(summary)
    st.markdown("</div>", unsafe_allow_html=True)

