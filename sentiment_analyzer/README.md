# Sentiment Analyzer

A simple web application that performs sentiment analysis on text using Hugging Face's transformers library. The application uses the DistilBERT model fine-tuned for sentiment analysis.

## Features

- Clean, modern UI built with TailwindCSS
- Real-time sentiment analysis
- Displays sentiment (POSITIVE/NEGATIVE) and confidence score
- Error handling and user feedback

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Enter or paste your text in the input field
2. Click "Analyze Sentiment"
3. View the results showing the sentiment (POSITIVE/NEGATIVE) and the confidence score

## Technical Details

- Backend: Flask (Python)
- Frontend: HTML, JavaScript, TailwindCSS
- Model: DistilBERT (fine-tuned for sentiment analysis)
- Libraries: transformers, torch

## Note

The first time you run the application, it will download the model files from Hugging Face, which might take a few moments depending on your internet connection. 