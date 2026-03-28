 Automated Podcast Transcription and Topic Segmentation

 About the Project
This project focuses on converting podcast audio into readable text automatically. 
Listening to long podcasts takes time, so this system helps users quickly understand the content by generating transcripts, dividing them into topics, and showing summaries and visual insights.

The application allows users to explore podcast discussions easily through an interactive interface.


 Project Goal
The main goal of this project is to make podcast content easier to search, read, and analyze without listening to the entire audio.


 What the System Does
- Converts podcast audio into text
- Splits transcripts into meaningful topic sections
- Generates short summaries
- Performs sentiment analysis
- Extracts important keywords
- Displays keyword cloud and timeline visualization
- Provides an interactive Streamlit dashboard



 Dataset
Podcast audio files were collected from online sources.

- Audio format: MP3 (converted to WAV during processing)
- Multiple podcast episodes were used
- Audio was cleaned and divided into smaller chunks before transcription



 Tools Used
- **Whisper** – for speech-to-text transcription
- **LibROSA & PyDub** – for audio processing
- **TF-IDF** – for keyword extraction
- **TextBlob** – for sentiment analysis
- **WordCloud & Matplotlib** – for visualization
- **Streamlit** – for building the user interface



 How the Project Works
1. The user selects a podcast audio file.
2. The audio is preprocessed and split into parts.
3. Speech is converted into text using Whisper.
4. The transcript is divided into topics.
5. Summaries and sentiment scores are generated.
6. Keywords and visualizations are displayed in the interface.



 How to Run the Project
1. Install required libraries:
   pip install -r requirements.txt

2. Run the application:
   streamlit run app.py



 Output
The system displays:
- Full transcript
- Topic-wise navigation
- Summaries
- Sentiment analysis
- Keyword WordCloud
- Interactive visual dashboard



 Limitations
- Transcription accuracy depends on audio clarity
- Background noise may affect results
- Topic segmentation is not always perfect



 Future Improvements
- Real-time transcription
- Speaker identification
- Better summarization models
- Improved user interface



 Author
Ayinavalli Amrutha Varshini
(Automated Podcast Transcription and Topic Segmentation)