document.addEventListener("DOMContentLoaded", function () {
    const assistant = document.getElementById("assistant-ia");
    const closeButton = document.getElementById("assistant-ia-close");
    const form = document.getElementById("assistant-ia-form");
    const input = document.getElementById("assistant-ia-input");
    const messages = document.getElementById("assistant-ia-messages");
    const submitButton = form?.querySelector('button[type="submit"]');
    const csrfToken = form?.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    );

    if (
        !assistant ||
        !closeButton ||
        !form ||
        !input ||
        !messages ||
        !submitButton ||
        !csrfToken
    ) {
        return;
    }

    let previousFocus = null;
    let requestInProgress = false;

    const conversationStorageKey = "assistant-1j1s-conversation";

    function saveConversationMessage(role, content) {
        try {
            const history = JSON.parse(
                sessionStorage.getItem(conversationStorageKey) || "[]"
            );
    
            history.push({ role: role, content: content });
    
            sessionStorage.setItem(
                conversationStorageKey,
                JSON.stringify(history)
            );
        } catch (error) {
            console.warn("Impossible de sauvegarder la conversation.");
        }
    }

    // Ouvrir automatiquement l'assistant sur ordinateur.
    if (window.matchMedia("(min-width: 992px)").matches) {
        assistant.hidden = false;
    }

    
    function openAssistant() {
        previousFocus = document.activeElement;
        assistant.hidden = false;
        input.focus();
    }

    function closeAssistant() {
        assistant.hidden = true;

        if (previousFocus && previousFocus.isConnected) {
            previousFocus.focus();
        }
    }

    function addMessage(content, className) {
        const message = document.createElement("p");
        message.textContent = content;
        message.className = className;

        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;

        return message;
    }

    document.querySelectorAll("[data-assistant-open]").forEach(function (button) {
        button.addEventListener("click", openAssistant);
    });

    closeButton.addEventListener("click", closeAssistant);

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !assistant.hidden) {
            closeAssistant();
        }
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const question = input.value.trim();

        if (!question || requestInProgress) {
            return;
        }

        requestInProgress = true;
        submitButton.disabled = true;

        addMessage(question, "fr-text--md");
        saveConversationMessage("user", question);
        input.value = "";

        const waitingMessage = addMessage(
            "L'assistant prépare sa réponse…",
            "fr-text--sm"
        );

        try {
            const response = await fetch("/assistant/chat/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken.value
                },
                body: JSON.stringify({
                    message: question
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Une erreur est survenue."
                );
            }

            waitingMessage.innerHTML =
                data.answer_html || "L'assistant n'a pas retourné de réponse.";

        } catch (error) {
            waitingMessage.textContent =
                error.message || "Impossible de contacter l'assistant.";

        } finally {
            requestInProgress = false;
            submitButton.disabled = false;
            messages.scrollTop = messages.scrollHeight;
            input.focus();
        }
    });
});
