// web_interface/static/js/chat.js

document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const typingIndicatorContainer = document.getElementById('typing-indicator-container');

    // Function to show/hide the typing indicator
    const showTypingIndicator = () => {
        typingIndicatorContainer.innerHTML = `
            <div class="bot-avatar">TC</div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        typingIndicatorContainer.classList.add('show');
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    const hideTypingIndicator = () => {
        typingIndicatorContainer.classList.remove('show');
    };

    // Function to add a message to the chat box
    const addMessage = (message, isUser) => {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('message-wrapper');
        messageWrapper.classList.add(isUser ? 'user' : 'bot');

        if (!isUser) {
            const avatar = document.createElement('div');
            avatar.classList.add('bot-avatar');
            avatar.textContent = 'TC'; // For Tata Capital
            messageWrapper.appendChild(avatar);
        }

        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        messageElement.innerHTML = message.replace(/\n/g, '<br>');
        messageWrapper.appendChild(messageElement);

        // Add timestamp
        const timestamp = document.createElement('div');
        timestamp.classList.add('timestamp');
        const now = new Date();
        timestamp.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        messageWrapper.appendChild(timestamp);

        chatBox.appendChild(messageWrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // --- NEW: Function to create and display the pre-approval banner ---
    const showPreApprovalBanner = (customerName, limit) => {
        const bannerWrapper = document.createElement('div');
        bannerWrapper.classList.add('message-wrapper', 'bot');

        const avatar = document.createElement('div');
        avatar.classList.add('bot-avatar');
        avatar.textContent = 'TC';
        bannerWrapper.appendChild(avatar);

        const bannerElement = document.createElement('div');
        bannerElement.classList.add('pre-approval-banner');
        bannerElement.innerHTML = `
            <div class="banner-header">Congratulations, ${customerName}! 🎉</div>
            <div class="banner-body">
                You are pre-approved for a personal loan up to
                <div class="banner-amount">₹${limit.toLocaleString('en-IN')}</div>
            </div>
        `;

        bannerWrapper.appendChild(bannerElement);
        chatBox.appendChild(bannerWrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Function to send a message to the backend
    const sendMessage = async () => {
        const message = messageInput.value.trim();
        if (message === '') return;

        // Display user's message
        addMessage(message, true);
        messageInput.value = '';

        // Show the typing indicator
        showTypingIndicator();

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
            
            // Hide the typing indicator before showing the response
            hideTypingIndicator();

            // --- NEW: Check if the backend wants to show the pre-approval banner ---
            if (data.show_pre_approval_banner) {
                // Display the initial text message
                addMessage(data.message, false);
                
                // Show the special pre-approval banner
                showPreApprovalBanner(data.customer_name, data.pre_approved_limit);
                
                // Update the state and ask the next question after a short delay
                setTimeout(() => {
                    addMessage("How much would you like to borrow? (e.g., 500000)", false);
                }, 1500);

            } else {
                // Handle normal bot response (including download links)
                const botMessage = data.message;

                // Check if the message contains a download link marker
                if (typeof botMessage === 'string' && botMessage.includes("||DOWNLOAD_LINK:")) {
                    const parts = botMessage.split("||DOWNLOAD_LINK:");
                    const messageText = parts[0];
                    const filename = parts[1].replace('||', '');

                    // Display the main message
                    if (messageText) {
                        addMessage(messageText, false);
                    }

                    // Create and add the download button inside a new message bubble
                    const messageWrapper = document.createElement('div');
                    messageWrapper.classList.add('message-wrapper', 'bot');

                    const avatar = document.createElement('div');
                    avatar.classList.add('bot-avatar');
                    avatar.textContent = 'TC';
                    messageWrapper.appendChild(avatar);

                    const messageElement = document.createElement('div');
                    messageElement.classList.add('message', 'bot-message');
                    
                    const downloadLink = document.createElement('a');
                    downloadLink.href = `/download_letter/${encodeURIComponent(filename)}`;
                    downloadLink.className = 'download-button'; // Use class for styling
                    downloadLink.textContent = 'Download Your Sanction Letter';
                    downloadLink.setAttribute('download', filename);

                    messageElement.appendChild(downloadLink);
                    messageWrapper.appendChild(messageElement);

                    // Add timestamp
                    const timestamp = document.createElement('div');
                    timestamp.classList.add('timestamp');
                    const now = new Date();
                    timestamp.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    messageWrapper.appendChild(timestamp);

                    chatBox.appendChild(messageWrapper);
                    chatBox.scrollTop = chatBox.scrollHeight;

                } else {
                    // Display a normal bot response
                    addMessage(botMessage, false);
                }
            }

        } catch (error) {
            hideTypingIndicator();
            console.error('Error:', error);
            addMessage('Sorry, something went wrong. Please try again.', false);
        }
    };

    // Event listeners for the send button and Enter key
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) { // Allow new lines with Shift+Enter
            event.preventDefault();
            sendMessage();
        }
    });

    // Initial greeting from the bot
    addMessage("Welcome to Tata Capital! I'm here to help you with your personal loan needs. To get started, could you please provide your 10-digit mobile number?", false);
});