import os
import pandas as pd
from flask import Flask, jsonify, render_template, request, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from clean_text import clean_text


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "any-key-you-like-for-dev")  # In production, set this to a secure random value

data = pd.read_csv("Mental_Health_FAQ.csv")

questions = list(data['Questions'].apply(clean_text))
answers = list(data['Answers'].fillna('').astype(str))

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(questions)

FALLBACK_RESPONSE = (
    "I'm here for you. I couldn't find a confident answer to that yet. "
    "Could you rephrase your question or share a little more detail?"
)


def get_best_answer(question: str):
    clean_question = clean_text(question)
    question_tfidf = vectorizer.transform([clean_question])
    similarities = cosine_similarity(question_tfidf, tfidf_matrix)
    best_match_idx = int(similarities.argmax())
    confidence = float(similarities[0, best_match_idx])

    if confidence < 0.15:
        return FALLBACK_RESPONSE, confidence
    return answers[best_match_idx], confidence

@app.route('/', methods=['POST', 'GET'])
def index():
    history = session.get('history', [])
    return render_template('index.html', history=history)


@app.route('/ask', methods=['POST'])
def ask():
    payload = request.get_json(silent=True) or {}
    question = (payload.get('question') or '').strip()

    if not question:
        return jsonify({'error': 'Please enter a question.'}), 400

    answer, confidence = get_best_answer(question)

    history = session.get('history', [])
    history.append({
        'question': question,
        'answer': answer,
        'confidence': round(confidence, 3)
    })

    # Keep only the latest messages to avoid an oversized session.
    session['history'] = history[-12:]

    return jsonify({
        'question': question,
        'answer': answer,
        'confidence': round(confidence, 3)
    })


if __name__ == '__main__':
    app.run(debug=True)