document.addEventListener("DOMContentLoaded", function() {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatLog = document.getElementById('chat-log');
    const questionDropdown = document.getElementById('question-dropdown');
    const profileImageUrl = document.body.getAttribute('data-profile-url');

    loadChatHistory();
    userInput.focus();

    sendButton.addEventListener('click', sendMessage);
    document.getElementById("clear-button").addEventListener("click", clearChatHistory);
    userInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
    questionDropdown.addEventListener('change', function() {
        const selectedQuestion = questionDropdown.value;
        if (selectedQuestion) {
            userInput.value = selectedQuestion;
            sendButton.click();
        }
        questionDropdown.value = ''; // Reset dropdown value
        userInput.value = ''; // Clear the input box
        userInput.focus();    // Focus the input box
        saveChatHistory();
    });

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user-message', true);
        toggleInput(false);
        if (!message.includes('/correct')) {
            setTimeout(() => {addTypingIndicator(); }, 250);
        }

        userInput.value = ''; // Clear the input box

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            removeTypingIndicator();
            addMessage(data.answer, 'bot-message', true);
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage('Sorry, something went wrong. Please try again later.', 'bot-message', true);
        } finally {
            toggleInput(true);
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

    function addTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'chat-message bot-message typing-indicator';
        typingIndicator.id = 'typing-indicator';
        
        const imgElement = document.createElement('img');
        imgElement.src = profileImageUrl; // Profile picture
        typingIndicator.appendChild(imgElement);

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = 'Typing...';

        typingIndicator.appendChild(messageContent);
        chatLog.appendChild(typingIndicator);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            chatLog.removeChild(typingIndicator);
        }
    }

    function toggleInput(enabled) {
        userInput.disabled = !enabled;
        sendButton.disabled = !enabled;
        questionDropdown.disabled = !enabled;
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
    
                    // Send a request to the server to clear the chat history
                    fetch('/clear_history', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    }).then(response => {
                        return response.json();
                    }).then(data => {
                        if (data.success) {
                            console.log("Chat history successfully cleared on the server."); // Success log
                        } else {
                            console.log("Failed to clear chat history on the server."); // Error log
                        }
                    }).catch(error => {
                        console.error('Error clearing chat history on the server:', error); // Error handling log
                    });
                }
            });
        });
        userInput.focus();
    }   
});
