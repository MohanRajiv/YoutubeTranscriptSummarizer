"""Utility functions for handling YouTube transcripts."""
import re
from typing import List, Tuple, Dict, Any

def search_keyword_print_startimes(transcript: List[Dict[str, Any]], search_word: str) -> Tuple[List[float], List[str]]:
    """Search for a keyword in the transcript and return timestamps and lines."""
    data = [t['text'] for t in transcript]
    data = [re.sub(r"[^a-zA-Z0-9 ]", "", line) for line in data]
    
    time = []
    lines = []
    for i, line in enumerate(data):
        if search_word in line:
            start_time = transcript[i]['start']
            time.append(start_time)
            lines.append(line)
    
    return time, lines

def extract_transcript_details(
    youtube_video_url: str,
    start_time: float | None = None,
    end_time: float | None = None
) -> str | None:
    """Extract transcript details from a YouTube video."""
    from youtube_transcript_api import YouTubeTranscriptApi
    
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        
        total_duration = transcript_text[-1]['start'] + transcript_text[-1]['duration']

        if start_time is None and end_time is None:
            transcript = " ".join(i["text"] for i in transcript_text)
            return transcript
        
        if start_time < 0 or end_time < start_time or end_time > total_duration:
            raise ValueError("Invalid timestamps. Please enter valid start and end times.")

        filtered_transcript = " ".join(
            i["text"] for i in transcript_text
            if start_time <= i['start'] <= end_time
        )
        return filtered_transcript

    except Exception as e:
        raise Exception(f"Error extracting transcript: {str(e)}")

def generate_chapters(transcript_text: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate chapters from transcript text."""
    try:
        total_duration = sum(segment['duration'] for segment in transcript_text)
        chapters = {}
        chapter_start = 0
        chapter_end = 60

        while chapter_end <= total_duration:
            chapter_text = " ".join(
                segment['text'] for segment in transcript_text
                if segment['start'] >= chapter_start and segment['start'] <= chapter_end
            )
            chapters[f"Chapter {chapter_start}-{chapter_end}"] = chapter_text
            chapter_start = chapter_end
            chapter_end += 60
        
        return chapters
    except Exception as e:
        raise Exception(f"Error generating chapters: {str(e)}") 