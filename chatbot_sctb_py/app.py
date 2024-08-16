from flask import Flask, request, jsonify, render_template
from chatbot import handle_query  # Import the handle_query function from chatbot.py
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

if __name__ == '__main__':
    app.run(debug=False)
