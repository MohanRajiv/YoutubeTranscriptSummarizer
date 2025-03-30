# YouTube Transcript Summarizer

A Streamlit application that allows you to summarize YouTube videos using Google's Gemini AI. The application can:
- Summarize entire videos
- Summarize specific segments of videos
- Search for keywords in video transcripts
- Generate chapter-based summaries

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Google API key for Gemini AI

## Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd youtube-transcript-summarizer
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies using uv:
```bash
uv pip install -e .
```

4. Create a `.env` file in the root directory with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run src/app.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Enter a YouTube video URL and choose your desired mode:
   - Whole Video: Summarize the entire video
   - Specific Timestamps: Summarize a specific segment
   - Search Keyword: Search for specific keywords in the transcript

## Features

- Beautiful dark-themed UI
- Real-time video thumbnail preview
- Configurable summary length
- Keyword search with timestamp tracking
- Chapter-based summarization
- Error handling and user feedback

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 