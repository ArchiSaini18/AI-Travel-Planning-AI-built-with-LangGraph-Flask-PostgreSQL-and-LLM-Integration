let currentUser = null;
let currentTrip = null;
let selectedVibe = 'solo';

document.addEventListener('DOMContentLoaded', async () => {
    await loadUser();
    await loadTrips();
    setupEvents();
});

async function loadUser() {
    try {
        const response = await fetch('/api/auth/current-user');
        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('user-avatar').textContent = currentUser.username[0].toUpperCase();
            document.getElementById('user-name').textContent = `@${currentUser.username}`;
        } else {
            window.location.href = '/login';
        }
    } catch {
        window.location.href = '/login';
    }
}

async function loadTrips() {
    try {
        const response = await fetch('/api/conversations');
        if (response.ok) {
            const data = await response.json();
            const trips = data.conversations || [];
            const tripsList = document.getElementById('trips-list');
            
            if (tripsList) {
                tripsList.innerHTML = '';
                if (trips.length === 0) {
                    tripsList.innerHTML = '<p style="font-size: 13px; color: #999; padding: 8px;">No trips yet</p>';
                } else {
                    trips.forEach(trip => {
                        const item = document.createElement('div');
                        item.className = 'conversation-item';
                        item.innerHTML = `
                            <div style="flex: 1; cursor: pointer;" onclick="loadTrip(${trip.id})">
                                <div style="font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                    ${trip.title || 'Untitled Trip'}
                                </div>
                                <div style="font-size: 12px; color: #999; margin-top: 2px;">
                                    ${new Date(trip.updated_at).toLocaleDateString()}
                                </div>
                            </div>
                            <span class="conversation-delete" onclick="deleteTrip(event, ${trip.id})" title="Delete">×</span>
                        `;
                        tripsList.appendChild(item);
                    });
                }
            }
        }
    } catch (error) {
        console.error('Error loading trips:', error);
    }
}

async function loadTrip(tripId) {
    try {
        currentTrip = tripId;
        const response = await fetch(`/api/conversations/${tripId}`);
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById('messages-container');
            if (container) {
                container.innerHTML = '';
                const messages = data.messages || [];
                messages.forEach(msg => {
                    addMessage(msg.content, msg.role);
                });
                container.scrollTop = container.scrollHeight;
            }
        }
    } catch (error) {
        console.error('Error loading trip:', error);
    }
}

async function deleteTrip(e, tripId) {
    e.stopPropagation();
    if (confirm('Delete this trip?')) {
        try {
            await fetch(`/api/conversations/${tripId}`, { method: 'DELETE' });
            if (currentTrip === tripId) {
                newTrip();
            }
            await loadTrips();
        } catch (error) {
            console.error('Error deleting trip:', error);
        }
    }
}

function setupEvents() {
    const form = document.getElementById('chat-form');
    if (form) {
        form.addEventListener('submit', sendMessage);
    }
    
    const quickForm = document.getElementById('quick-form');
    if (quickForm) {
        quickForm.addEventListener('submit', quickPlan);
    }
    
    const userAvatar = document.getElementById('user-avatar');
    if (userAvatar) {
        userAvatar.addEventListener('click', () => {
            const dropdown = document.getElementById('dropdown-menu');
            if (dropdown) {
                dropdown.classList.toggle('active');
            }
        });
    }
}

async function quickPlan(e) {
    e.preventDefault();
    const destination = document.getElementById('quick-destination').value;
    const days = document.getElementById('quick-days').value;
    const vibe = document.getElementById('quick-vibe').value;

    const message = `I want a ${days}-day ${vibe} trip to ${destination}. Please create a personalized itinerary.`;
    document.getElementById('message-input').value = message;
    
    const event = new Event('submit');
    const form = document.getElementById('chat-form');
    if (form) {
        await sendMessage({preventDefault: () => {}});
    }
}

function selectVibe(vibeType) {
    selectedVibe = vibeType;
    document.querySelectorAll('.vibe-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (event && event.target) {
        event.target.classList.add('active');
    }
}

function selectDestination(destination) {
    document.getElementById('quick-destination').value = destination;
    document.getElementById('quick-destination').focus();
}

async function sendMessage(e) {
    if (e.preventDefault) e.preventDefault();

    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) {
        alert('Please enter a message');
        return;
    }

    addMessage(message, 'user');
    input.value = '';
    input.focus();

    showTyping();

    try {
        if (!currentTrip) {
            currentTrip = await createTrip(message);
        }

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_id: currentTrip,
                message: message,
                user_id: currentUser.id
            })
        });

        hideTyping();

        if (!response.ok) {
            const errorData = await response.json();
            addMessage(`Error: ${errorData.error || 'Failed to process request'}`, 'assistant');
            return;
        }

        const data = await response.json();

        if (data.response) {
            addMessage(data.response, 'assistant');
        } else {
            addMessage('No response received. Please try again.', 'assistant');
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
        hideTyping();
        console.error('Chat error:', error);
        addMessage(`Error: ${error.message || 'Failed to process your request. Please try again.'}`, 'assistant');
    }
}

function addMessage(content, role) {
    const container = document.getElementById('messages-container');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-${role === 'user' ? 'user' : 'plane'}"></i>
        </div>
        <div class="message-bubble">${escapeHtml(content)}</div>
    `;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showTyping() {
    const container = document.getElementById('messages-container');
    if (!container) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'message assistant';
    typingDiv.innerHTML = `
        <div class="message-avatar"><i class="fas fa-plane"></i></div>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

function hideTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}

async function createTrip(title) {
    try {
        const response = await fetch('/api/conversations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title.substring(0, 50) })
        });
        if (response.ok) {
            const data = await response.json();
            return data.id;
        } else {
            throw new Error('Failed to create trip');
        }
    } catch (error) {
        console.error('Create trip error:', error);
        throw error;
    }
}

function displayDestination(dest) {
    const content = document.getElementById('destination-content');
    if (!content) return;
    
    const bestSeasons = dest.best_seasons ? (Array.isArray(dest.best_seasons) ? dest.best_seasons.join(', ') : dest.best_seasons) : 'Year-round';
    
    content.innerHTML = `
        <div class="info-item">
            <div class="info-label">📍 Destination</div>
            <div class="info-value">${dest.name || 'Unknown'}, ${dest.country || ''}</div>
        </div>
        <div class="info-item">
            <div class="info-label">🌤️ Best Season</div>
            <div class="info-value">${bestSeasons}</div>
        </div>
    `;
    document.getElementById('destination-panel').style.display = 'block';
}

function displayWeather(weather) {
    const content = document.getElementById('weather-content');
    if (!content) return;
    
    let html = `
        <div class="info-item">
            <div class="info-label">🌡️ Current</div>
            <div class="info-value">${weather.current?.temperature || 'N/A'}°C</div>
        </div>
    `;
    
    if (weather.forecast && Array.isArray(weather.forecast)) {
        weather.forecast.slice(0, 3).forEach(day => {
            html += `
                <div class="info-item">
                    <div class="info-label">${day.date || 'Day'}</div>
                    <div class="info-value">${day.temp_max || '?'}°/${day.temp_min || '?'}°C</div>
                </div>
            `;
        });
    }
    
    content.innerHTML = html;
    document.getElementById('weather-panel').style.display = 'block';
}

function displayBudget(budget) {
    const content = document.getElementById('budget-content');
    if (!content) return;
    
    const symbol = budget.currency_symbol || '$';
    
    content.innerHTML = `
        <div class="info-item">
            <div class="info-label">💰 Total Budget</div>
            <div class="info-value">${symbol}${budget.total || '0'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">📅 Per Day</div>
            <div class="info-value">${symbol}${budget.daily_average || '0'}</div>
        </div>
    `;
    document.getElementById('budget-panel').style.display = 'block';
}

function newTrip() {
    currentTrip = null;
    const container = document.getElementById('messages-container');
    if (container) {
        container.innerHTML = `
            <div class="message assistant">
                <div class="message-avatar"><i class="fas fa-plane"></i></div>
                <div class="message-bubble">
                    <p><strong>✨ Ready for your next adventure?</strong></p>
                    <p style="margin-top: 8px; opacity: 0.9;">Tell me where you'd like to go and what kind of experience you're looking for!</p>
                </div>
            </div>

            <div style="margin-top: 30px; margin-bottom: 15px;">
                <h3 style="color: #333; font-size: 16px; font-weight: 700;"><i class="fas fa-globe"></i> Popular Destinations</h3>
            </div>
            <div class="destination-showcase">
                <div class="destination-preview" onclick="selectDestination('Bali')">
                    <div class="destination-preview-img">🏝️</div>
                    <div class="destination-preview-info">
                        <h4>Bali</h4>
                        <div class="destination-preview-tags">
                            <span class="destination-preview-tag">Beach</span>
                            <span class="destination-preview-tag">Relax</span>
                        </div>
                    </div>
                </div>
                <div class="destination-preview" onclick="selectDestination('Paris')">
                    <div class="destination-preview-img">🗼</div>
                    <div class="destination-preview-info">
                        <h4>Paris</h4>
                        <div class="destination-preview-tags">
                            <span class="destination-preview-tag">Romance</span>
                            <span class="destination-preview-tag">Culture</span>
                        </div>
                    </div>
                </div>
                <div class="destination-preview" onclick="selectDestination('Tokyo')">
                    <div class="destination-preview-img">🗾</div>
                    <div class="destination-preview-info">
                        <h4>Tokyo</h4>
                        <div class="destination-preview-tags">
                            <span class="destination-preview-tag">Culture</span>
                            <span class="destination-preview-tag">Food</span>
                        </div>
                    </div>
                </div>
                <div class="destination-preview" onclick="selectDestination('Dubai')">
                    <div class="destination-preview-img">🏙️</div>
                    <div class="destination-preview-info">
                        <h4>Dubai</h4>
                        <div class="destination-preview-tags">
                            <span class="destination-preview-tag">Luxury</span>
                            <span class="destination-preview-tag">Modern</span>
                        </div>
                    </div>
                </div>
                <div class="destination-preview" onclick="selectDestination('Switzerland')">
                    <div class="destination-preview-img">🏔️</div>
                    <div class="destination-preview-info">
                        <h4>Switzerland</h4>
                        <div class="destination-preview-tags">
                            <span class="destination-preview-tag">Adventure</span>
                            <span class="destination-preview-tag">Nature</span>
                        </div>
                    </div>
                </div>
                <div class="destination-preview" onclick="selectDestination('Thailand')">
                    <div class="destination-preview-img">🌴</div>
                    <div class="destination-preview-info">
                        <h4>Thailand</h4>
                        <div class="destination-preview-tags">
                            <span class="destination-preview-tag">Adventure</span>
                            <span class="destination-preview-tag">Food</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    const destPanel = document.getElementById('destination-panel');
    const weatherPanel = document.getElementById('weather-panel');
    const budgetPanel = document.getElementById('budget-panel');
    
    if (destPanel) destPanel.style.display = 'none';
    if (weatherPanel) weatherPanel.style.display = 'none';
    if (budgetPanel) budgetPanel.style.display = 'none';
}

function showMyTrips(e) {
    e.preventDefault();
    const dropdown = document.getElementById('dropdown-menu');
    if (dropdown) dropdown.classList.remove('active');
    
    const tripsList = document.getElementById('trips-list');
    if (tripsList) {
        tripsList.scrollIntoView({ behavior: 'smooth', block: 'center' });
        tripsList.style.backgroundColor = 'rgba(0, 102, 204, 0.1)';
        setTimeout(() => {
            tripsList.style.backgroundColor = '';
        }, 2000);
    }
}

function showSettings(e) {
    e.preventDefault();
    const dropdown = document.getElementById('dropdown-menu');
    if (dropdown) dropdown.classList.remove('active');
    alert('Settings:\n\n📱 Theme: Light\n🌍 Language: English\n🔔 Notifications: Enabled\n\nMore settings coming soon!');
}

async function logout(e) {
    e.preventDefault();
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = '/login';
    }
}
