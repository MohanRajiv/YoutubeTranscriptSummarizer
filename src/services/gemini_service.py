"""Service for handling Gemini AI operations."""
import re
import google.generativeai as genai
from typing import List, Dict, Any

class GeminiService:
    def __init__(self, api_key: str):
        """Initialize the Gemini service with API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def generate_content(self, transcript_text: str, prompt: str, max_words: int) -> str:
        """Generate content using Gemini AI."""
        response = self.model.generate_content(prompt + transcript_text)
        
        # Split the text into sentences
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', response.text)
        
        # Collect sentences until reaching max_words
        word_count = 0
        summary_sentences = []
        for sentence in sentences:
            words = sentence.split()
            if word_count + len(words) <= max_words:
                summary_sentences.append(sentence)
                word_count += len(words)
            else:
                break
        
        return ' '.join(summary_sentences) 