require('dotenv').config();
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*" }  // Prod: ["https://your-streamlit-app.streamlit.app"]
});

const onlineUsers = new Map();  // username → socket.id

app.get('/', (req, res) => res.send('Socket.IO Chat Backend Running'));

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  socket.on('register', (username) => {
    if (onlineUsers.has(username)) {
      socket.emit('usernameTaken');
      return;
    }
    onlineUsers.set(username, socket.id);
    socket.username = username;
    io.emit('onlineUsers', Array.from(onlineUsers.keys()));
    socket.emit('registered');
  });

  socket.on('private message', ({ to, text }) => {
    const toId = onlineUsers.get(to);
    if (toId) {
      const msg = { from: socket.username, text, time: new Date().toLocaleTimeString() };
      io.to(toId).emit('private message', msg);
      socket.emit('private message', { ...msg, self: true });
    } else {
      socket.emit('userOffline', to);
    }
  });

  socket.on('disconnect', () => {
    if (socket.username) {
      onlineUsers.delete(socket.username);
      io.emit('onlineUsers', Array.from(onlineUsers.keys()));
    }
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server on port ${PORT}`));