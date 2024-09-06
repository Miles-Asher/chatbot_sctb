// Language translations data
const translations = {
    en: {
        questionDropdown: [
            "Select an FAQ...",
            "Where do I get on the bus?",
            "Can I get back on after getting off the bus?",
            "Are bus seats assigned?",
            "What type of buses do you run?",
            "Does the bus tour operate in the rain?",
            "What time does the Downtown Palace Namsan Course bus depart?",
            "How long does the Downtown Palace Namsan Course take?",
            "Is there a washroom on the bus?",
            "What is your cancellation/refund policy?"
        ],
        inputPlaceholder: "Type a message...",
        sendButton: "Send",
        clearButton: "Clear History",
        typingIndicator: "Typing..."
    },
    ko: {
        questionDropdown: [
            "FAQ를 선택하세요...",
            "버스에 어디서 탑승하나요?",
            "버스에서 내린 후 다시 탑승할 수 있나요?",
            "좌석이 지정되어 있나요?",
            "어떤 종류의 버스를 운행하나요?",
            "비가 와도 버스 투어가 운영되나요?",
            "도심 궁궐 남산 코스 버스는 몇 시에 출발하나요?",
            "도심 궁궐 남산 코스는 얼마나 걸리나요?",
            "버스에 화장실이 있나요?",
            "취소/환불 정책은 무엇인가요?"
        ],
        inputPlaceholder: "메시지를 입력하세요...",
        sendButton: "전송",
        clearButton: "기록 지우기",
        typingIndicator: "입력중..."
    },
    ja: {
        questionDropdown: [
            "FAQを選択してください...",
            "バスにはどこで乗れますか?",
            "バスを降りた後に再び乗車できますか?",
            "座席は指定されていますか?",
            "どのようなタイプのバスを運行していますか?",
            "雨が降ってもバスツアーは運行されますか?",
            "市内観光コースバスは何時に出発しますか?",
            "市内観光コースにはどのくらいかかりますか?",
            "バスにトイレはありますか?",
            "キャンセル/返金ポリシーは何ですか?"
        ],
        inputPlaceholder: "メッセージを入力...",
        sendButton: "送信",
        clearButton: "履歴をクリア",
        typingIndicator: "入力中..."
    },
    zh: {
        questionDropdown: [
            "选择一个常见问题...",
            "在哪里上车?",
            "下车后还能重新上车吗?",
            "座位是指定的吗?",
            "你们运行什么类型的巴士?",
            "下雨时巴士之旅还会运行吗?",
            "市中心宫殿南山路线的巴士什么时候出发?",
            "市中心宫殿南山路线需要多长时间?",
            "巴士上有洗手间吗?",
            "取消/退款政策是什么?"
        ],
        inputPlaceholder: "输入消息...",
        sendButton: "发送",
        clearButton: "清除历史记录",
        typingIndicator: "输入中..."
    }
};

let currentLanguage = 'ko'; // Default language

function changeLanguage(lang) {
    currentLanguage = lang; // Update the current language
    const translation = translations[lang];

    // Update the question dropdown options
    const questionDropdown = document.getElementById("question-dropdown");

    // Update the default option text
    const defaultOption = questionDropdown.options[0]; // Get the existing default option
    defaultOption.textContent = translation.questionDropdown[0]; // Update it with the translated text

    // Clear all options except the first one (default)
    questionDropdown.options.length = 1;

    // Add the rest of the options
    translation.questionDropdown.slice(1).forEach((text) => {
        const option = document.createElement("option");
        option.value = text;
        option.textContent = text;
        questionDropdown.appendChild(option);
    });

    // Reset the dropdown to show the default option
    questionDropdown.value = "";
    
    // Update the input placeholder
    const userInput = document.getElementById("user-input");
    userInput.placeholder = translation.inputPlaceholder;

    // Update the Send and Clear History buttons
    const sendButton = document.getElementById("send-button");
    sendButton.textContent = translation.sendButton;

    const clearButton = document.getElementById("clear-button");
    clearButton.textContent = translation.clearButton;
}

// Event listener for language icon click
document.getElementById("language-icon").addEventListener("click", function() {
    var dropdown = document.getElementById("dropdown-content");
    if (dropdown.style.display === "block") {
        dropdown.style.display = "none";
    } else {
        dropdown.style.display = "block";
    }
});

// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('#language-icon')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.style.display === "block") {
                openDropdown.style.display = "none";
            }
        }
    }
};

// Existing chatbot functionality
document.addEventListener("DOMContentLoaded", function() {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatLog = document.getElementById('chat-log');
    const questionDropdown = document.getElementById('question-dropdown');
    const profileImageUrl = document.body.getAttribute('data-profile-url');
    const chatbotButton = document.getElementById('chatbot-button');
    const chatContainer = document.querySelector('.chat-container');

    // Set default language to Korean
    changeLanguage('ko');

    // Add event listener to toggle chat container visibility
    chatbotButton.addEventListener("click", function() {
        if (chatContainer.style.display === "none" || chatContainer.style.display === "") {
            chatContainer.style.display = "flex"; // Show the chat container
        } else {
            chatContainer.style.display = "none"; // Hide the chat container
        }
    });

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
        questionDropdown.value = ''; // Reset dropdown to default option
        userInput.value = ''; // Clear the input box
        userInput.focus();    // Focus the input box
        saveChatHistory();
    });

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
    
        addMessage(message, 'user-message', true);
        toggleInput(false);
        
        // Check if the message contains the /correct command
        if (message.includes('/correct')) {
            const password = prompt("Please enter the password:");
    
            // Verify the password before proceeding
            const correctPassword = 'sctb'; // Replace with your actual password
    
            if (password !== correctPassword) {
                addMessage('Incorrect password. Command not executed.', 'bot-message', true);
                toggleInput(true);
                userInput.focus();    // Focus the input box
                return;
            }
        } else {
            setTimeout(() => { addTypingIndicator(); }, 250);
        }
    
        userInput.value = ''; // Clear the input box
    
        try {
            const response = await fetch("chat.php", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `message=${encodeURIComponent(message)}`
            })
            ;
            
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
        messageContent.textContent = translations[currentLanguage].typingIndicator; // Use translated text

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
