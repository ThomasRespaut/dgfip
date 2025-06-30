// Configuration de l'API Django
const API_BASE_URL = '/api/chat/';

// Base FAQ locale
const localFaqData = {
    "comment déclarer mes revenus": "Pour déclarer vos revenus, connectez-vous à votre espace particulier sur impots.gouv.fr...",
    "dates limites déclaration": "Les dates limites de déclaration 2024 (revenus 2023) sont : • Déclaration papier : 18 mai 2024...",
    "modifier mon taux de prélèvement": "Vous pouvez modifier votre taux de prélèvement à la source dans votre espace particulier...",
    "payer mes impôts en ligne": "Le paiement en ligne est possible via votre espace particulier...",
    "contester un avis d'imposition": "Pour contester un avis d'imposition, vous avez jusqu'au 31 décembre...",
    "prélèvement à la source": "Le prélèvement à la source collecte l'impôt directement sur votre salaire...",
    "simulation impôt": "L'outil de simulation sur impots.gouv.fr vous permet d'estimer votre impôt...",
    "erreur déclaration": "Si vous découvrez une erreur après validation, vous pouvez la corriger en ligne...",
    "crédit d'impôt": "Les crédits d'impôt sont remboursés si leur montant dépasse l'impôt dû...",
    "quotient familial": "Le quotient familial réduit l'impôt selon votre situation familiale...",
};

// Utilitaires
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}

function findLocalFallback(userInput) {
    const input = userInput.toLowerCase();
    let bestMatch = "default";
    let maxScore = 0;

    for (let key in localFaqData) {
        if (key === "default") continue;
        const keywords = key.split(" ");
        let score = keywords.reduce((acc, word) => acc + input.includes(word), 0);
        if (score > maxScore) {
            maxScore = score;
            bestMatch = key;
        }
    }
    return localFaqData[bestMatch];
}

// Appel API Django (fallback géré côté serveur)
async function callChatAPI(message) {
    const response = await fetch(API_BASE_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ message: message })
    });

    if (!response.ok) {
        throw new Error(`Erreur HTTP ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
        return {
            response: data.response,
            source: data.source,
            contexts_used: data.contexts_used || 0
        };
    } else {
        throw new Error(data.error || "Erreur inconnue");
    }
}

// UI Chat
function addMessage(content, isUser = false, metadata = {}) {
    const container = document.getElementById('chatMessages');
    const msg = document.createElement('div');
    msg.className = `message ${isUser ? 'user' : 'bot'}`;

    const now = new Date();
    const time = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });

    let source = '';
    if (!isUser && metadata.source) {
        const icons = {
            'faq_basic': '📚', 'mistral_rag': '🧠', 'context_fallback': '📄',
            'local_fallback': '💾', 'no_context': '❓', 'error': '❗'
        };
        const icon = icons[metadata.source] || '🤖';
        source = `<small style="opacity: 0.7;">${icon} Source: ${metadata.source}</small>`;
    }

    msg.innerHTML = `
        <div class="message-avatar">${isUser ? '👤' : '🤖'}</div>
        <div class="message-content">
            ${content}
            ${source}
            <div class="message-time">${time}</div>
        </div>
    `;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const typing = document.createElement('div');
    typing.className = 'message bot';
    typing.id = 'typingIndicator';
    typing.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="typing-indicator">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            <small style="margin-left: 10px; opacity: 0.7;">Recherche en cours...</small>
        </div>
    `;
    container.appendChild(typing);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
}

// Gestion envoi message
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const btn = document.getElementById('sendButton');
    const message = input.value.trim();
    if (!message) return;

    btn.disabled = true;
    btn.innerHTML = '⏳';
    addMessage(message, true);
    input.value = '';
    adjustTextareaHeight(input);
    showTypingIndicator();

    const result = await callChatAPI(message);
    removeTypingIndicator();
    addMessage(result.response, false, {
        source: result.source,
        contexts_used: result.contexts_used,
        error: result.error
    });

    btn.disabled = false;
    btn.innerHTML = '▶️';
}

function sendSuggestion(s) {
    document.getElementById('chatInput').value = s;
    sendMessage();
}

function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function adjustTextareaHeight(t) {
    t.style.height = 'auto';
    t.style.height = Math.min(t.scrollHeight, 120) + 'px';
}

// Démarrage
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        addMessage(
            "🔄 <strong>Système avancé activé !</strong><br><br>" +
            "Je suis maintenant connecté à une base de données vectorielle complète et au modèle Mistral pour vous aider.<br><br>" +
            "Posez-moi vos questions sur la fiscalité !",
            false,
            { source: 'system' }
        );
    }, 1500);

    const closeBtn = document.querySelector('.close-alert');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            document.querySelector('.alert-banner').style.display = 'none';
        });
    }
});
