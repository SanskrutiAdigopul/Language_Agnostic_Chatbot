// ---------------- Language Dropdown ----------------
function toggleDropdown() {
  const dropdown = document.getElementById('language-dropdown');
  dropdown.classList.toggle('show');
}

function selectLanguage(language) {
  document.getElementById('selected-language').textContent = language;
  document.getElementById('language-dropdown').classList.remove('show');
  console.log(`Language changed to: ${language}`);
}

// Close dropdown when clicking outside
window.onclick = function (event) {
  if (!event.target.matches('.dropdown-btn') && !event.target.matches('.dropdown-btn *')) {
    const dropdown = document.getElementById('language-dropdown');
    if (dropdown.classList.contains('show')) {
      dropdown.classList.remove('show');
    }
  }
};

// ---------------- Chat Functionality ----------------
function addMessage(text, sender) {
  const messagesContainer = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender}`;

  const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  messageDiv.innerHTML = `
    <div>${text}</div>
    <div class="message-time">${currentTime}</div>
  `;

  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById('message-input');
  const message = input.value.trim();
  if (message === '') return;

  // Add user message
  addMessage(message, 'user');
  input.value = '';

  // Get selected language
  const selectedLanguage = document.getElementById('selected-language').textContent;

  // Prepare form data
  const formData = new FormData();
  formData.append("query", message);
  formData.append("top_k", "3");
  formData.append("lang", selectedLanguage);

  try {
    const res = await fetch("/chat/query", {
      method: "POST",
      body: formData
    });
    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }
    const data = await res.json();
    addMessage(data.response, 'bot');
  } catch (error) {
    console.error("Chat request failed:", error);
    addMessage("⚠️ Error contacting server", 'bot');
  }
}

// ---------------- Init ----------------
document.addEventListener('DOMContentLoaded', () => {
  console.log('Language Agnostic Chatbot initialized');

  const input = document.getElementById('message-input');
  const sendBtn = document.getElementById('send-btn');

  // Send on Enter
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });

  // Send on button click
  sendBtn.addEventListener('click', sendMessage);
});