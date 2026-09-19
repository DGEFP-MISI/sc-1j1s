document.addEventListener("DOMContentLoaded", function () {
    const assistant = document.getElementById("assistant-ia");
    const closeButton = document.getElementById("assistant-ia-close");
    const form = document.getElementById("assistant-ia-form");
    const input = document.getElementById("assistant-ia-input");
    const messages = document.getElementById("assistant-ia-messages");

    if (!assistant || !closeButton || !form || !input || !messages) {
        return;
    }

    let previousFocus = null;

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

    // Permet d'ouvrir l'assistant depuis n'importe quel bouton
    // possédant l'attribut data-assistant-open.

    document.querySelectorAll("[data-assistant-open]").forEach(function (button) {
        button.addEventListener("click", openAssistant);
    });

    closeButton.addEventListener("click", closeAssistant);

    // Fermeture avec la touche Échap.

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !assistant.hidden) {
            closeAssistant();
        }
    });

    // Première version du formulaire.
    // L'appel à Albert API sera ajouté ultérieurement.

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const question = input.value.trim();

        if (!question) {
            return;
        }

        const message = document.createElement("p");
        message.textContent = question;
        message.className = "fr-text--md";

        messages.appendChild(message);

        input.value = "";
        messages.scrollTop = messages.scrollHeight;
    });
});
