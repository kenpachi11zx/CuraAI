const chatForm = document.getElementById("chat-form");
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendButton = document.querySelector(".send-button");
const welcomeScreen = document.getElementById("welcome-screen");
const chatHistory = document.querySelector(".chat-history");

let isTyping = false;
let hasStartedChat = false;
let currentChatId = null;
let chatHistoryData = [];

document.addEventListener("DOMContentLoaded", () => {
  loadChatHistory();
  userInput.focus();
  
  document.body.style.opacity = '0';
  setTimeout(() => {
    document.body.style.transition = 'opacity 0.5s ease-in-out';
    document.body.style.opacity = '1';
  }, 100);
  
  setupKeyboardNavigation();
});

function loadChatHistory() {
  const saved = localStorage.getItem('curaai_chat_history');
  if (saved) {
    chatHistoryData = JSON.parse(saved);
    renderChatHistory();
  }
}

function saveChatHistory() {
  localStorage.setItem('curaai_chat_history', JSON.stringify(chatHistoryData));
}

function createNewChat() {
  const chatId = Date.now().toString();
  const newChat = {
    id: chatId,
    title: 'New Chat',
    timestamp: new Date().toISOString(),
    messages: []
  };
  
  chatHistoryData.unshift(newChat);
  currentChatId = chatId;
  saveChatHistory();
  renderChatHistory();
  return chatId;
}

function renderChatHistory() {
  if (chatHistoryData.length === 0) {
    chatHistory.innerHTML = `
      <div class="empty-state">
        <h3>Nothing here yet</h3>
        <p>Your health consultations will appear here</p>
      </div>
    `;
    return;
  }

  const historyHTML = chatHistoryData.map(chat => {
    const date = new Date(chat.timestamp).toLocaleDateString();
    const time = new Date(chat.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const isActive = chat.id === currentChatId;
    
    return `
      <div class="chat-item ${isActive ? 'active' : ''}" onclick="loadChat('${chat.id}')">
        <div class="chat-item-content">
          <div class="chat-title">${chat.title}</div>
          <div class="chat-meta">${date} at ${time}</div>
        </div>
        <button class="delete-chat-btn" onclick="deleteChat('${chat.id}', event)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
          </svg>
        </button>
      </div>
    `;
  }).join('');

  chatHistory.innerHTML = historyHTML;
}

function loadChat(chatId) {
  const chat = chatHistoryData.find(c => c.id === chatId);
  if (!chat) return;

  currentChatId = chatId;
  
  chatBox.innerHTML = '';
  welcomeScreen.style.display = 'none';
  
  chat.messages.forEach(message => {
    appendMessage(message.sender, message.text, false);
  });
  
  renderChatHistory();
  scrollToBottom();
}

function deleteChat(chatId, event) {
  event.stopPropagation();
  
  const index = chatHistoryData.findIndex(chat => chat.id === chatId);
  if (index > -1) {
    chatHistoryData.splice(index, 1);
    saveChatHistory();
    renderChatHistory();
    
    if (currentChatId === chatId) {
      startNewChat();
    }
  }
}

function updateChatTitle(chatId, title) {
  const chat = chatHistoryData.find(c => c.id === chatId);
  if (chat) {
    chat.title = title;
    saveChatHistory();
    renderChatHistory();
  }
}

function addMessageToHistory(sender, text) {
  if (currentChatId) {
    const chat = chatHistoryData.find(c => c.id === currentChatId);
    if (chat) {
      chat.messages.push({ sender, text });
      saveChatHistory();
      
      if (chat.messages.length === 2 && chat.title === 'New Chat') {
        const firstMessage = chat.messages[0].text.substring(0, 50);
        updateChatTitle(currentChatId, firstMessage + (firstMessage.length === 50 ? '...' : ''));
      }
    }
  }
}

function quickAction(type) {
  const messages = {
    'headache': 'I have a headache',
    'fever': 'I have a fever',
    'stomach': 'I have stomach pain',
    'firstaid': 'I need a first aid kit'
  };
  
  if (messages[type]) {
    userInput.value = messages[type];
    chatForm.dispatchEvent(new Event('submit'));
  }
}

function startNewChat() {
  currentChatId = createNewChat();
  
  chatBox.innerHTML = '';
  welcomeScreen.style.display = 'none';
  
  hasStartedChat = true;
  userInput.focus();
  
  renderChatHistory();
}

function appendMessageWithTyping(sender, text) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${sender}`;
  
  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  
  if (sender === 'ai') {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
      <div class="typing-content">
        <div class="typing-dots">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    `;
    contentDiv.appendChild(typingDiv);
  } else {
    contentDiv.textContent = text;
  }
  
  messageDiv.appendChild(contentDiv);
  chatBox.appendChild(messageDiv);
  
  scrollToBottom();
  
  if (sender === 'ai') {
    setTimeout(() => {
      removeTypingIndicator();
      appendMessage(sender, text);
    }, 1000 + Math.random() * 2000);
  }
}

function appendMessage(sender, text, saveToHistory = true) {
  if (saveToHistory) {
    addMessageToHistory(sender, text);
  }
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${sender}`;
  
  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  
  if (sender === 'ai') {
    contentDiv.innerHTML = formatAIResponse(text);
  } else {
    contentDiv.textContent = text;
  }
  
  messageDiv.appendChild(contentDiv);
  chatBox.appendChild(messageDiv);
  
  scrollToBottom();
}

function formatAIResponse(text) {
  const lines = text.split('\n');
  let formattedText = '';
  
  lines.forEach(line => {
    if (line.trim()) {
      if (line.startsWith('Possible Cause:') || line.startsWith('Recommended Steps:') || 
          line.startsWith('Medications:') || line.startsWith('When to See a Doctor:')) {
        formattedText += `<p><strong>${line}</strong></p>`;
      } else {
        formattedText += `<p>${line}</p>`;
      }
    }
  });
  
  return formattedText;
}

function showTypingIndicator() {
  if (!isTyping) {
    isTyping = true;
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message ai typing-indicator';
    typingDiv.innerHTML = `
      <div class="message-content">
        <div class="typing-content">
          <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      </div>
    `;
    chatBox.appendChild(typingDiv);
    scrollToBottom();
  }
}

function removeTypingIndicator() {
  const typingIndicator = document.querySelector('.typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
    isTyping = false;
  }
}

function setInputState(enabled) {
  userInput.disabled = !enabled;
  sendButton.disabled = !enabled;
  
  if (enabled) {
    userInput.focus();
  }
}

function scrollToBottom() {
  setTimeout(() => {
    chatBox.scrollTop = chatBox.scrollHeight;
  }, 100);
}

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const message = userInput.value.trim();
  if (!message || isTyping) return;
  
  if (!hasStartedChat) {
    startNewChat();
  }
  
  appendMessage('user', message);
  userInput.value = '';
  
  setInputState(false);
  showTypingIndicator();
  
  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    removeTypingIndicator();
    appendMessage('ai', data.reply);
    
  } catch (error) {
    console.error('Error:', error);
    removeTypingIndicator();
    showErrorWithRetry('Sorry, there was an error. Please try again.');
  } finally {
    setInputState(true);
  }
});

function showErrorWithRetry(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.innerHTML = `
    <p>${message}</p>
    <button onclick="retryLastMessage()">Retry</button>
  `;
  chatBox.appendChild(errorDiv);
  scrollToBottom();
}

function retryLastMessage() {
  const errorMessage = document.querySelector('.error-message');
  if (errorMessage) {
    errorMessage.remove();
  }
  
  const lastUserMessage = document.querySelector('.chat-message.user:last-child');
  if (lastUserMessage) {
    const messageText = lastUserMessage.querySelector('.message-content').textContent;
    userInput.value = messageText;
    chatForm.dispatchEvent(new Event('submit'));
  }
}

function setupKeyboardNavigation() {
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      userInput.blur();
    }
    
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event('submit'));
    }
  });
}

function addHapticFeedback() {
  if ('vibrate' in navigator) {
    navigator.vibrate(10);
  }
}

window.quickAction = quickAction;
window.startNewChat = startNewChat;
window.loadChat = loadChat;
window.deleteChat = deleteChat;
window.retryLastMessage = retryLastMessage;
