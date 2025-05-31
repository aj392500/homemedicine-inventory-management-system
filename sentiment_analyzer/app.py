from flask import Flask, render_template, request, jsonify
from textblob import TextBlob

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Perform sentiment analysis using TextBlob
        analysis = TextBlob(text)
        
        # Convert polarity to sentiment label
        if analysis.sentiment.polarity > 0:
            sentiment = "POSITIVE"
        elif analysis.sentiment.polarity < 0:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        
        # Convert polarity to percentage (0-100 scale)
        score = (abs(analysis.sentiment.polarity) * 100)
        
        return jsonify({
            'sentiment': sentiment,
            'score': f"{score:.2f}%"
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 