let currentUser = null;
let currentConversationId = null;
let conversationHistory = [];

document.addEventListener('DOMContentLoaded', async () => {
    await loadCurrentUser();
    await loadConversations();
    setupEventListeners();
});

async function loadCurrentUser() {
    try {
        const response = await fetch('/api/auth/current-user');
        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('user-avatar').textContent = currentUser.username[0].toUpperCase();
            document.getElementById('user-name').textContent = `@${currentUser.username}`;
        } else {
            window.location.href = '/login';
        }
    } catch (error) {
        window.location.href = '/login';
    }
}

async function loadConversations() {
    try {
        const response = await fetch(`/api/conversations`);
        if (response.ok) {
            conversationHistory = await response.json();
            renderConversations();
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

function renderConversations() {
    const container = document.getElementById('conversations-list');
    container.innerHTML = '';

    conversationHistory.forEach(conv => {
        const div = document.createElement('div');
        div.className = 'conversation-item' + (conv.id === currentConversationId ? ' active' : '');
        div.innerHTML = `
            <span onclick="loadConversation(${conv.id})">${conv.title}</span>
            <span class="conversation-delete" onclick="deleteConversation(${conv.id})">
                <i class="fas fa-trash"></i>
            </span>
        `;
        container.appendChild(div);
    });
}

function setupEventListeners() {
    document.getElementById('chat-form').addEventListener('submit', sendMessage);
    document.getElementById('user-avatar').addEventListener('click', toggleDropdown);
}

function toggleDropdown() {
    document.getElementById('dropdown-menu').classList.toggle('active');
}

async function sendMessage(e) {
    e.preventDefault();

    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) return;

    addMessage(message, 'user');
    input.value = '';

    showTypingIndicator();

    try {
        if (!currentConversationId) {
            currentConversationId = await createConversation(message);
        }

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                message: message,
                user_id: currentUser.id
            })
        });

        const data = await response.json();
        hideTypingIndicator();

        if (data.response) {
            addMessage(data.response, 'assistant');
        }

        if (data.destination) {
            displayDestination(data.destination);
        }

        if (data.weather) {
            displayWeather(data.weather);
        }

        if (data.budget) {
            displayBudget(data.budget);
        }

    } catch (error) {
        hideTypingIndicator();
        addMessage('Sorry, an error occurred. Please try again.', 'assistant');
    }
}

function addMessage(content, role) {
    const container = document.getElementById('messages-container');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-${role === 'user' ? 'user' : 'plane'}"></i>
        </div>
        <div class="message-bubble">${content}</div>
    `;

    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator.innerHTML = `
        <div class="message assistant">
            <div class="message-avatar">
                <i class="fas fa-plane"></i>
            </div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').innerHTML = '';
}

async function createConversation(firstMessage) {
    const response = await fetch('/api/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: firstMessage.substring(0, 50) })
    });

    const data = await response.json();
    await loadConversations();
    return data.id;
}

async function loadConversation(id) {
    currentConversationId = id;
    renderConversations();

    const response = await fetch(`/api/conversations/${id}`);
    const data = await response.json();

    const container = document.getElementById('messages-container');
    container.innerHTML = '';

    data.messages.forEach(msg => {
        addMessage(msg.content, msg.role);
    });
}

async function deleteConversation(id) {
    if (confirm('Delete this conversation?')) {
        await fetch(`/api/conversations/${id}`, { method: 'DELETE' });
        if (currentConversationId === id) {
            currentConversationId = null;
            document.getElementById('messages-container').innerHTML = '';
        }
        await loadConversations();
    }
}

function newChat() {
    currentConversationId = null;
    document.getElementById('messages-container').innerHTML = `
        <div class="message assistant">
            <div class="message-avatar">
                <i class="fas fa-plane"></i>
            </div>
            <div class="message-bubble">
                <p>Hi! I'm your AI Travel Planner. Tell me about your dream trip!</p>
            </div>
        </div>
    `;
    renderConversations();
}

function displayDestination(destination) {
    const panel = document.getElementById('destination-panel');
    const content = document.getElementById('destination-content');

    content.innerHTML = `
        <div class="info-item">
            <div class="info-label">Destination</div>
            <div class="info-value">${destination.name}, ${destination.country}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Best Season</div>
            <div class="info-value">${destination.best_seasons?.join(', ')}</div>
        </div>
    `;

    panel.style.display = 'block';
}

function displayWeather(weather) {
    const panel = document.getElementById('weather-panel');
    const content = document.getElementById('weather-content');

    let html = `
        <div class="info-item">
            <div class="info-label">Current</div>
            <div class="info-value">${weather.current.temperature}°C</div>
        </div>
    `;

    weather.forecast?.slice(0, 3).forEach(day => {
        html += `
            <div class="info-item">
                <div class="info-label">${day.date}</div>
                <div class="info-value">${day.temp_max}°/${day.temp_min}°C</div>
            </div>
        `;
    });

    content.innerHTML = html;
    panel.style.display = 'block';
}

function displayBudget(budget) {
    const panel = document.getElementById('budget-panel');
    const content = document.getElementById('budget-content');

    content.innerHTML = `
        <div class="info-item">
            <div class="info-label">Total</div>
            <div class="info-value">${budget.currency_symbol}${budget.total}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Daily</div>
            <div class="info-value">${budget.currency_symbol}${budget.daily_average}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Accommodation</div>
            <div class="info-value">${budget.currency_symbol}${budget.accommodation}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Food</div>
            <div class="info-value">${budget.currency_symbol}${budget.food}</div>
        </div>
    `;

    panel.style.display = 'block';
}

async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/login';
}
