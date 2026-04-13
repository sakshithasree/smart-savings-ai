function setPrompt(text) {
    const input = document.getElementById("userInput");
    input.value = text;
    input.focus();
}

function appendMessage(text, sender = "user") {
    const chatBody = document.getElementById("chatBody");
    const message = document.createElement("div");
    message.className = `chat-message ${sender}-message`;

    if (sender === "user") {
        message.innerHTML = `
            <div class="chat-bubble user-bubble">
                <div class="message-label">You</div>
                <p>${text}</p>
            </div>
        `;
    } else {
        message.innerHTML = `
            <div class="chat-icon">
                <div class="icon-circle">🤖</div>
            </div>
            <div class="chat-bubble">
                <div class="message-label">AI Assistant</div>
                <p>${text}</p>
            </div>
        `;
    }

    chatBody.appendChild(message);
    chatBody.scrollTop = chatBody.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById("userInput");
    const userText = input.value.trim();
    if (!userText) return;

    appendMessage(userText, "user");
    input.value = "";

    try {
        const response = await fetch("/assistant-chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: userText })
        });

        const data = await response.json();
        appendMessage(data.reply, "assistant");
    } catch (error) {
        appendMessage("Sorry, something went wrong while processing your request.", "assistant");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("sendBtn");
    const userInput = document.getElementById("userInput");

    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
    }

    if (userInput) {
        userInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                sendMessage();
            }
        });
    }
});