// Store chat history
let chatHistory = [];

// Function to add a message to the chat
function addMessage(content, isUser = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = isUser ? 'U' : 'B';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = content;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to history
    chatHistory.push({
        role: isUser ? 'user' : 'bot',
        content: content
    });
}

// Function to show/hide typing indicator
function setTypingIndicator(show) {
    const indicator = document.getElementById('typing-indicator');
    if (show) {
        indicator.classList.add('active');
    } else {
        indicator.classList.remove('active');
    }
}

async function checkFact() {
    const queryInput = document.getElementById("query");
    const sendButton = document.getElementById("send-button");
    const query = queryInput.value.trim();

    if (!query) {
        return;
    }

    // Disable input and button
    queryInput.disabled = true;
    sendButton.disabled = true;

    // Add user message
    addMessage(query, true);

    // Clear input
    queryInput.value = '';

    // Show typing indicator
    setTypingIndicator(true);

    try {
        const response = await fetch("/fact-check", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Failed to check fact");
        }

        // Add bot response
        addMessage(data.response);

    } catch (error) {
        // Add error message
        addMessage(`<span style="color: #dc3545;">Error: ${error.message}</span>`);
    } finally {
        // Hide typing indicator
        setTypingIndicator(false);
        
        // Re-enable input and button
        queryInput.disabled = false;
        sendButton.disabled = false;
        queryInput.focus();
    }
}

// Add enter key support
document.getElementById("query").addEventListener("keypress", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        checkFact();
    }
});

// Focus input on page load
window.addEventListener('load', () => {
    document.getElementById("query").focus();
});
  