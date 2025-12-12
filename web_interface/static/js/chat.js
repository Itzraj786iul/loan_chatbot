document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');

    // Function to add a message to the chat box
    const addMessage = (message, isUser) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        // Handle newlines in bot messages
        messageElement.innerHTML = message.replace(/\n/g, '<br>');
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
    };

    // Function to send a message to the backend
    const sendMessage = async () => {
        const message = messageInput.value.trim();
        if (message === '') return;

        // Display user's message
        addMessage(message, true);
        messageInput.value = '';

        try {
            // Send message to the Flask backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            // Display bot's response
            addMessage(data.message, false);

        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, something went wrong. Please try again.', false);
        }
    };

    // Event listeners for the send button and Enter key
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Initial greeting from the bot
    addMessage("Welcome to Tata Capital! I'm here to help you with your personal loan needs. To get started, could you please provide your 10-digit mobile number?", false);
});