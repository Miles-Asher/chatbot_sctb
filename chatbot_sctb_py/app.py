from flask import Flask, request, jsonify, render_template
from chatbot import handle_query, clear_chat_history  # Import necessary functions from chatbot.py
import os

app = Flask(__name__)

# Initialize chat history
chat_history = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data['message']

    # Get the answer from the chatbot using handle_query
    answer = handle_query(question)
    
    return jsonify({"answer": answer})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    # Clear chat history by calling the function from chatbot.py
    clear_chat_history()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=False)
