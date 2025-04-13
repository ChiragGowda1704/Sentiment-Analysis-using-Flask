from flask import Flask, render_template, request
from textblob import TextBlob
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
import re

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    # Tiered word lists for precise scoring
    STRONG_POSITIVE = {
        'excellent', 'outstanding', 'brilliant', 'fantastic', 'amazing',
        'perfect', 'love', 'wonderful', 'superb', 'fabulous'
    }
    
    MODERATE_POSITIVE = {
        'good', 'great', 'happy', 'nice', 'pleasant',
        'satisfied', 'like', 'enjoy', 'pleased', 'delighted'
    }
    
    STRONG_NEGATIVE = {
        'hate', 'terrible', 'horrible', 'awful', 'disgusting',
        'worst', 'never', 'angry', 'disappointed', 'furious'
    }
    
    MODERATE_NEGATIVE = {
        'bad', 'sad', 'poor', 'upset', 'annoyed',
        'frustrated', 'tired', 'problem', 'issue', 'hard'
    }
    
    NEUTRAL_INDICATORS = {
        'okay', 'ok', 'fine', 'alright', 'maybe',
        'perhaps', 'think', 'guess', 'probably', 'possibly'
    }
    
    NEGATION_WORDS = {
        'not', "don't", "doesn't", "isn't", "wasn't",
        "can't", "won't", 'no', 'never', 'none'
    }

    CONTRAST_WORDS = {'but', 'however', 'although', 'though'}

    @staticmethod
    def analyze(text):
        """Perfect sentiment analysis handling all edge cases"""
        if not text or not isinstance(text, str) or len(text.strip()) < 3:
            return "Neutral", 50

        text_lower = text.lower()
        words = set(text_lower.split())
        
        # 1. Check for explicit negations first
        for neg in SentimentAnalyzer.NEGATION_WORDS:
            if neg in text_lower:
                # Check for negated positives ("not good")
                following_word = text_lower.split(neg)[-1].split()[0]
                if (following_word in SentimentAnalyzer.STRONG_POSITIVE or 
                    following_word in SentimentAnalyzer.MODERATE_POSITIVE):
                    return "Negative", 85
                # Check for negated negatives ("not bad")
                if following_word in SentimentAnalyzer.STRONG_NEGATIVE:
                    return "Positive", 70

        # 2. Handle contrast statements
        for contrast in SentimentAnalyzer.CONTRAST_WORDS:
            if contrast in text_lower:
                parts = text_lower.split(contrast)
                if len(parts) > 1:
                    _, conf1 = SentimentAnalyzer._analyze_segment(parts[0])
                    sentiment2, conf2 = SentimentAnalyzer._analyze_segment(parts[1])
                    return sentiment2, min(95, conf2 + 5)

        # 3. Analyze the complete text
        return SentimentAnalyzer._analyze_segment(text)

    @staticmethod
    def _analyze_segment(text):
        """Analyze individual text segments"""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Scoring system
        pos_score = 0
        neg_score = 0
        
        for word in words:
            if word in SentimentAnalyzer.STRONG_POSITIVE:
                pos_score += 3
            elif word in SentimentAnalyzer.MODERATE_POSITIVE:
                pos_score += 1
            elif word in SentimentAnalyzer.STRONG_NEGATIVE:
                neg_score += 3
            elif word in SentimentAnalyzer.MODERATE_NEGATIVE:
                neg_score += 1

        # Neutral word check
        neutral_words = sum(1 for word in words 
                          if word in SentimentAnalyzer.NEUTRAL_INDICATORS)
        
        # Decision logic
        if neutral_words >= 2 and abs(pos_score - neg_score) <= 1:
            return "Neutral", 50
            
        if neg_score > pos_score:
            confidence = min(95, 60 + neg_score * 10)
            return "Negative", confidence
            
        if pos_score > neg_score:
            confidence = min(95, 60 + pos_score * 10)
            return "Positive", confidence

        # TextBlob fallback with adjusted thresholds
        try:
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            if polarity > 0.2:
                return "Positive", 70
            elif polarity < -0.2:
                return "Negative", 70
            else:
                return "Neutral", 50
        except:
            return "Neutral", 50

@app.route("/", methods=["GET", "POST"])
def home():
    sentiment = None
    confidence = 50
    text = ""
    
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if text:
            sentiment, confidence = SentimentAnalyzer.analyze(text)
            confidence = max(5, min(95, confidence))  # Ensure reasonable bounds
    
    return render_template(
        "index.html",
        sentiment=sentiment,
        confidence=confidence,
        text=text
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)