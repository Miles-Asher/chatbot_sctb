document.addEventListener("DOMContentLoaded", function() {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const clearButton = document.getElementById('clear-button');
    const chatLog = document.getElementById('chat-log');
    const loadingIndicator = document.getElementById('loading-indicator');

    const profileImageUrl = document.body.getAttribute('data-profile-url');

    loadChatHistory();
    userInput.focus();

    sendButton.addEventListener('click', sendMessage);
    clearButton.addEventListener('click', clearChatHistory);
    userInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user-message', true);
        toggleLoadingIndicator(true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            addMessage(data.answer, 'bot-message', true);
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, something went wrong. Please try again later.', 'bot-message', true);
        } finally {
            toggleLoadingIndicator(false);
            userInput.value = ''; // Clear the input box
            userInput.focus();    // Focus the input box
            saveChatHistory();
        }
    }

    function addMessage(message, className, animate = false) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${className}`;
        if (animate) {
            messageElement.classList.add('animate-message');
        }

        if (className === 'bot-message') {
            const imgElement = document.createElement('img');
            imgElement.src = profileImageUrl; // Profile picture
            messageElement.appendChild(imgElement);
        }

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = message;
        
        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();

        messageContent.appendChild(timestamp);
        messageElement.appendChild(messageContent);
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;

        // Remove the animation class after the animation completes
        messageElement.addEventListener('animationend', () => {
            messageElement.classList.remove('animate-message');
        });
    }

    function toggleLoadingIndicator(show) {
        loadingIndicator.style.display = show ? 'block' : 'none';
    }

    function saveChatHistory() {
        localStorage.setItem('chatLog', chatLog.innerHTML);
    }

    function loadChatHistory() {
        const savedChatLog = localStorage.getItem('chatLog');
        if (savedChatLog) {
            chatLog.innerHTML = savedChatLog;
        }
    }

    function clearChatHistory() {
        const messages = chatLog.querySelectorAll('.chat-message');
        messages.forEach((message, index) => {
            message.classList.add('fade-out');
            message.addEventListener('animationend', () => {
                message.remove();
                if (index === messages.length - 1) {
                    chatLog.innerHTML = '';
                    localStorage.removeItem('chatLog');
                    userInput.focus();
                }
            });
        });
    }
});
