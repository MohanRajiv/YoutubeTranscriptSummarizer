"""Main Streamlit application for YouTube Transcript Summarizer."""
import os
from typing import List
import streamlit as st
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

from utils.transcript_utils import (
    search_keyword_print_startimes,
    extract_transcript_details,
    generate_chapters
)
from services.gemini_service import GeminiService

# Load environment variables
load_dotenv()

# Initialize Gemini service
gemini_service = GeminiService(api_key=os.getenv("GOOGLE_API_KEY"))

def print_time(search_word: str, time: List[float], lines: List[str]) -> None:
    """Print search results with timestamps."""
    st.write(f"'{search_word}' was mentioned at:")
    
    data = [["Start Times", "Sentence Mentioned"]]  # Title row
    for t, l in zip(time, lines):
        hours = int(t // 3600)
        minutes = int(t // 60)
        seconds = int(t % 60)
        data.append([f"{hours:02d}:{minutes:02d}:{seconds:02d}", l])
        
        with open("Output.txt", "a") as text_file:
            print(f"{hours:02d}:{minutes:02d}:{seconds:02d}", file=text_file)
    
    st.table(data)

def main():
    """Main application function."""
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
    
    youtube_link = st.text_input(
        "Enter YouTube Video Link:",
        help="Paste the link to the YouTube video."
    )

    if youtube_link:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

    # Sidebar options
    st.sidebar.title("Options")
    mode = st.sidebar.radio(
        "Select Mode",
        ("Whole Video", "Specific Timestamps", "Search Keyword"),
        help="Choose the mode of operation."
    )

    max_words = st.sidebar.number_input(
        "Maximum Number of Words for Summary:",
        min_value=10,
        max_value=1000,
        value=250,
        help="Enter the maximum number of words for the summary."
    )

    if mode == "Specific Timestamps":
        start_time_min = st.sidebar.number_input(
            "Start Time (in minutes):",
            help="Enter the start time of the segment."
        )
        end_time_min = st.sidebar.number_input(
            "End Time (in minutes):",
            help="Enter the end time of the segment."
        )
        
        start_time = start_time_min * 60
        end_time = end_time_min * 60
    elif mode == "Search Keyword":
        search_word = st.sidebar.text_input(
            "Enter Keyword to Search in Transcript:",
            ""
        )

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
                    summary = gemini_service.generate_content(transcript_text, default_prompt, max_words)
                    st.markdown("---")
                    st.markdown("### Video Summary:")
                    st.write(summary)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 