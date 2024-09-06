<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <!-- Point to the correct styles.css file directly -->
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap">
</head>
<body data-profile-url="tb-circle.png">  <!-- Direct image path -->
    <header>
        <div class="header-container">
            <h1>Chat with Seoul City Tour Bus</h1>
        </div>
    </header>

    <button id="chatbot-button">
        <!-- Direct path to chat icon -->
        <img src="chat-icon.png" alt="Chat Icon" id="chat-icon">
    </button>    

    <main>
        <div class="chat-container">
            <!-- Language selection dropdown -->
            <div class="language-dropdown">
                <!-- Direct path to language icon -->
                <img src="language-icon.png" alt="Language" id="language-icon">
                <div class="dropdown-content" id="dropdown-content">
                    <a href="#" onclick="changeLanguage('ko')">
                        <img src="flags/kr.png" alt="Korean Flag" class="flag-icon"> KO
                    </a>
                    <a href="#" onclick="changeLanguage('en')">
                        <img src="flags/en.png" alt="English Flag" class="flag-icon"> EN
                    </a>
                    <a href="#" onclick="changeLanguage('ja')">
                        <img src="flags/jp.png" alt="Japanese Flag" class="flag-icon"> JA
                    </a>
                    <a href="#" onclick="changeLanguage('zh')">
                        <img src="flags/ch.png" alt="Chinese Flag" class="flag-icon"> ZH
                    </a>
                </div>
            </div>
            <!-- Existing chat elements -->
            <select id="question-dropdown">
                <option value="">Select an FAQ...</option>
                <option value="Where do I get on the bus?">Where do I get on the bus?</option>
                <option value="Can I get back on after getting off the bus?">Can I get back on after getting off the bus?</option>
                <option value="Are bus seats assigned?">Are bus seats assigned?</option>
                <option value="What type of buses do you run?">What type of buses do you run?</option>
                <option value="Does the bus tour operate in the rain?">Does the bus tour operate in the rain?</option>
                <option value="What time does the Downtown Palace Namsan Course bus depart?">What time does the Downtown Palace Namsan Course bus depart?</option>
                <option value="How long does the Downtown Palace Namsan Course take?">How long does the Downtown Palace Namsan Course take?</option>
                <option value="Is there a washroom on the bus?">Is there a washroom on the bus?</option>
                <option value="What is your cancellation/refund policy?">What is your cancellation/refund policy?</option>
            </select>
            <div class="chat-log" id="chat-log"></div>
            <div class="chat-input-container">
                <div class="loading-indicator" id="loading-indicator" style="display: none;">Typing...</div>
                <input type="text" id="user-input" placeholder="Type a message...">
                <button id="send-button">Send</button>
                <button id="clear-button">Clear History</button>
            </div>
        </div>
    </main>
    <footer>
        <div class="footer-container">
            <p>&copy; 2024 Seoul City Tour Bus. All Rights Reserved.</p>
        </div>
    </footer>

    <!-- Point to the chatbot.js file directly -->
    <script src="chatbot.js"></script>
</body>
</html>
