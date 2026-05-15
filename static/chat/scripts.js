
document.addEventListener("DOMContentLoaded", function () {
    // Generates or retrieve UUID for the user
    function generateUUID() {
        return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
    }

    let user_uuid = localStorage.getItem("user_uuid");
    if (!user_uuid) {
        user_uuid = generateUUID();
        localStorage.setItem("user_uuid", user_uuid);
    }

    const sendButton = document.getElementById("send-button");
    const messageInput = document.getElementById("message-input");
    const messages = document.getElementById("messages");
    const menuButton = document.getElementById("menu-button");
    const sidebarContainer = document.getElementById("sidebar-container");
    const chatBackground = document.getElementById("chat-background");
    const themeLinks = document.querySelectorAll('#sidebar a[data-theme]');
    const themeStylesheet = document.getElementById('theme-style');
    menuButton.addEventListener('click', () => {
    sidebarContainer.classList.toggle("open");
    sidebarContainer.classList.toggle("hidden");
});
    function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
    }
    // Render history if provided
    if (typeof chatHistory !== "undefined" && Array.isArray(chatHistory)) {
        chatHistory.forEach(({ user, bot }) => {
            appendMessage("You", user);
            appendMessage("Bot", bot);
        });
        scrollToBottom();
    }

    sendButton.addEventListener("click", sendMessage);
    messageInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    messageInput.addEventListener("input", () => {
    if (messageInput.value.trim() !== "") {
        sendButton.classList.add("visible");
    } else {
        sendButton.classList.remove("visible");
    }
});


    // Theme switching
    themeLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const themeFile = this.getAttribute("data-theme");
            themeStylesheet.href = `/static/chat/${themeFile}`;
        });
    });

    function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    appendMessage("You", message);
    messageInput.value = "";

    // Show typing indicator
    document.getElementById("typing-indicator").style.display = "block";

    fetch("/chat/api/chat/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            message: message,
            uuid: user_uuid
        })
    })
    .then(response => response.json())
    .then(data => {
        // Hide typing indicator after response
        document.getElementById("typing-indicator").style.display = "none";

        appendMessage("Bot", data.response || "Sorry, no response.");
    })
    .catch(() => {
        // Hide typing indicator on error too
        document.getElementById("typing-indicator").style.display = "none";

        appendMessage("Bot", "Error contacting server.");
    });
}

    function appendMessage(sender, message) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");

    if (sender === "You") {
        messageElement.classList.add("user");
    } else {
        messageElement.classList.add("bot");
    }

    messageElement.textContent = `: `;
    messages.appendChild(messageElement);
    scrollToBottom();
}

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
