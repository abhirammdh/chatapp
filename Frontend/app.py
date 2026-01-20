import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Chat Frontend", layout="wide")

# Embedded HTML/CSS/JS (with localStorage for username remember/edit)
html_code = """
<!DOCTYPE html>
<html style="background: #0e1117; color: #fafafa; font-family: Arial;">
<head>
<style>
  #chat { max-width: 800px; margin: 0 auto; }
  #messages { height: 500px; overflow-y: scroll; border: 1px solid #444; padding: 10px; background: #111; border-radius: 10px; }
  .bubble { padding: 12px; border-radius: 18px; margin: 8px 0; max-width: 70%; }
  .sent { background: #6200ea; margin-left: auto; color: white; }
  .received { background: #333; color: white; }
  #input { width: 70%; padding: 10px; border-radius: 8px; border: 1px solid #444; background: #1a1a1a; color: white; }
  button { padding: 10px 20px; background: #6200ea; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 5px; }
  button:hover { background: #7c3aed; }
  #users { list-style: none; padding: 0; }
  #users li { cursor: pointer; padding: 5px; border-bottom: 1px solid #444; }
  #users li:hover { background: #333; }
  #username-section { margin-bottom: 10px; }
  #current-name { color: #6200ea; font-weight: bold; }
</style>
</head>
<body>
<div id="chat">
  <h2>Private Chat 💬</h2>
  <div id="username-section">
    <span id="current-name"></span>
    <button id="edit-btn" onclick="toggleEdit()" style="display: none;">Edit Name</button>
    <input id="username" placeholder="Your username" style="display: none;" />
    <button id="join-btn" onclick="register()" style="display: none;">Join</button>
  </div>
  <ul id="users"></ul>
  <div id="messages"></div>
  <br>
  <input id="to" placeholder="To username" /><input id="input" placeholder="Message..." /><button onclick="send()">Send</button>
</div>

<script src="http://localhost:3000/socket.io/socket.io.js"></script>
<script>
const socket = io('http://localhost:3000');  // Update to live backend URL for deploy
let myName = localStorage.getItem('chatUsername') || null;  // Load from localStorage
let currentTo = null;
const messagesDiv = document.getElementById('messages');
const usernameInput = document.getElementById('username');
const joinBtn = document.getElementById('join-btn');
const editBtn = document.getElementById('edit-btn');
const currentNameSpan = document.getElementById('current-name');

// Load saved username on page start
window.addEventListener('load', () => {
  if (myName) {
    showCurrentName();
  } else {
    showUsernameInput();
  }
});

function showUsernameInput() {
  usernameInput.style.display = 'inline';
  joinBtn.style.display = 'inline';
  editBtn.style.display = 'none';
  currentNameSpan.textContent = '';
  usernameInput.value = '';  // Clear for new user
  usernameInput.focus();
}

function showCurrentName() {
  currentNameSpan.textContent = `Logged in as: ${myName}`;
  usernameInput.style.display = 'none';
  joinBtn.style.display = 'none';
  editBtn.style.display = 'inline';
}

function toggleEdit() {
  if (myName) {
    // Allow editing: prefill with current, but don't save until re-register
    showUsernameInput();
    usernameInput.value = myName;  // Prefill for easy edit
  }
}

function register() {
  const name = usernameInput.value.trim();
  if (!name) return alert('Enter a username!');
  
  socket.emit('register', name);
  myName = name;
  localStorage.setItem('chatUsername', myName);  // Save to localStorage
}

socket.on('registered', () => {
  showCurrentName();  // Hide input, show name + edit btn
});

socket.on('usernameTaken', () => {
  alert('Username taken! Try another.');
  // Keep input visible for retry
});

socket.on('onlineUsers', users => {
  const ul = document.getElementById('users');
  ul.innerHTML = '';
  users.forEach(u => {
    if (u !== myName) {
      const li = document.createElement('li');
      li.textContent = u;
      li.onclick = () => { 
        currentTo = u; 
        document.getElementById('to').value = u; 
      };
      ul.appendChild(li);
    }
  });
});

function send() {
  const text = document.getElementById('input').value.trim();
  const to = currentTo || document.getElementById('to').value.trim();
  if (!text || !to || !myName) {
    alert('Enter message, select a user, and join first!');
    return;
  }
  socket.emit('private message', { to, text });
  document.getElementById('input').value = '';
}

socket.on('private message', msg => {
  const div = document.createElement('div');
  div.className = `bubble ${msg.self ? 'sent' : 'received'}`;
  div.innerHTML = `<strong>${msg.self ? 'You' : msg.from}</strong> (${msg.time}): ${msg.text}`;
  messagesDiv.appendChild(div);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
});

socket.on('userOffline', to => alert(`${to} is offline`));

// Enter key to send
document.getElementById('input').addEventListener('keypress', e => { 
  if (e.key === 'Enter') send(); 
});
</script>
</body>
</html>
"""

st.title("Streamlit Chat Frontend")
st.markdown("Backend running? Check console for connections. Username saves locally!")

# Render the embedded HTML/JS/CSS
components.html(html_code, height=700)

st.info("👉 Enter username (saves automatically) → Join → Select user → Send (real-time!). Reload page — name remembers. Edit anytime!")