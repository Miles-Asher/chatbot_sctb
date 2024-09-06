
# chatbot_sctb

## Overview
**chatbot_sctb** is a user-friendly chatbot designed to answer specific questions about Seoul City Tour Bus services. It also provides personalized recommendations for cafes, restaurants, tourist attractions, and information about businesses around the tour routes. The chatbot is implemented via a Flask application hosted on an AWS EC2 instance, accessible at [http://15.165.204.98](http://15.165.204.98). 

This chatbot can also be integrated into other web and mobile applications using PHP or React via POST requests through cURL. It supports multiple languages and retains conversation history to provide context-aware responses.

---

## Features
- **Question Answering:** Searches a CSV file of frequently asked questions and answers from Seoul City Tour Bus customer service.
- **Question Correction:** Users can update or correct the chatbot's responses by sending a message in the format `/correct <question> | <answer>`.
- **Website Integration:** Searches the official Seoul City Tour Bus website to find answers to complex questions.
- **Business Recommendations:** Provides recommendations on local businesses (cafes, restaurants, attractions) using a custom API.
- **Multilingual Support:** Supports Korean, English, Japanese, and Chinese. The chatbot responds in the same language as the user's input.
- **Message History:** Saves conversation history for contextual replies and allows users to manually clear the history.
- **User Interface:** Includes a built-in UI that allows users to interact directly with the chatbot.

---

## Technologies Used
### Backend
- **Python:** Core language used for building chatbot logic
- **Packages:**
  - `Langchain`
  - `Flask`
  - `OpenAI`
  - `SentenceTransformer`
  - `BeautifulSoup`
  - `urllib.request`
  - `requests`
  - `json`
  - `pandas`
  - `numpy`
  - `dotenv`
  
### Frontend
- **HTML, CSS, JavaScript:** Used for the built-in chatbot UI
- **PHP (optional):** Example implementation included for web pages.

---

## Installation Instructions

### Clone the Repository
Clone the project from the following repository:
```bash
git clone https://github.com/Miles-Asher/chatbot_sctb
```

### Running Locally
1. Navigate to the Flask app directory:
   ```bash
   cd ./chatbot_sctb_py/
   ```
2. Run the Flask app:
   ```bash
   python app.py
   ```

### Accessing API Endpoints
Flask API endpoints are accessible via [http://15.165.204.98](http://15.165.204.98), which can be used for chatbot implementation in web or mobile apps.

---

## Usage Instructions

### Built-in UI
1. Click the chat icon button in the bottom right corner of the page to open the chat container.
2. Type a question in the input box and click **Send** to prompt the chatbot for a response.
3. Optionally, select a question from the FAQ dropdown if available.
4. Change the UI language by clicking the globe icon in the top right corner of the chat container.
5. Click **Clear History** to wipe the chat history and reset the chat.

### POST Request Implementation
For custom web or mobile app integration, send POST requests to the following URL:
```bash
http://15.165.204.98/chat
```
Include your message in the request, and the chatbot's response will be returned in JSON format. This can be processed within your app as needed.

### Example cURL Command
```bash
curl -X POST http://15.165.204.98/chat \
-H "Content-Type: application/json" \
-d '{"message": "Tell me about Seoul City Tour Bus."}'
```

---

## Configuration

If running the project locally, ensure you configure your OpenAI API key as an environment variable in a `.env` file located in `/chatbot_sctb_py/`:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

## Testing
Testing is best performed by running the chatbot locally and interacting with it through the built-in UI. If the chatbot consistently provides incorrect responses, you can correct the answers by sending the following message format:
```
/correct <question> | <answer>
```
This will update the chatbot’s CSV file, ensuring more accurate future responses to similar questions.

---

## Contributing Guidelines
Contributions are welcome! Feel free to modify and customize the source code as needed for your use case. 

For any questions, concerns, or discovered bugs, please reach out via email at:
**milesasher88@gmail.com**

---

## License
This project is open-source and available under the [MIT License](LICENSE).

---

## Author
**Miles Asher** - [milesasher88@gmail.com]
