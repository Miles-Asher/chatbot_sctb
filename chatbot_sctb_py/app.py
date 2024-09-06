from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS
from chatbot import handle_query, clear_chat_history  # Import necessary functions from chatbot.py
import os

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Initialize chat history
chat_history = []

# Home route to render the index.html page
@app.route('/')
def home():
    return render_template('index.html')

# Chat route to handle chatbot queries
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data['message']

    # Get the answer from the chatbot using handle_query
    answer = handle_query(question)
    
    return jsonify({"answer": answer})

# Route to clear chat history
@app.route('/clear_history', methods=['POST'])
def clear_history():
    # Clear chat history by calling the function from chatbot.py
    clear_chat_history()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=False)
