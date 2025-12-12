// web_interface/static/js/chat.js

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
            const botMessage = data.message;

            // Check if the message contains a download link marker
            // Expected format from backend: "Some text... ||DOWNLOAD_LINK:filename.pdf"
            if (typeof botMessage === 'string' && botMessage.includes("||DOWNLOAD_LINK:")) {
                const parts = botMessage.split("||DOWNLOAD_LINK:");
                const messageText = parts[0];
                const filename = parts[1].replace('||', ''); // <-- THIS IS THE FIX

                // Display the main message (if any)
                if (messageText) {
                    addMessage(messageText, false);
                }

                // Create and add the download button/link
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', 'bot-message');

                const downloadLink = document.createElement('a');
                // Ensure the backend route /download_letter/<filename> serves the file
                downloadLink.href = `/download_letter/${encodeURIComponent(filename)}`;
                downloadLink.textContent = 'Download Your Sanction Letter';
                downloadLink.setAttribute('download', filename); // hint to browser
                downloadLink.style.display = 'block';
                downloadLink.style.textAlign = 'center';
                downloadLink.style.marginTop = '10px';
                downloadLink.style.color = '#007bff';
                downloadLink.style.textDecoration = 'none';
                downloadLink.style.fontWeight = 'bold';

                messageElement.appendChild(downloadLink);
                chatBox.appendChild(messageElement);
                chatBox.scrollTop = chatBox.scrollHeight;

            } else {
                // Display a normal bot response
                addMessage(botMessage, false);
            }

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
