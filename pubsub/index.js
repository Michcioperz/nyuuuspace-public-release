const Redis = require('ioredis'), fs = require('fs');
var redis = new Redis({db: process.env.REDIS_DB});

var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);

redis.on('message', function (channel, message) {
  if (channel == 'hugs') {
    let msg = JSON.parse(message);
    io.to(msg.channel).emit('hug', msg.content);
  }
});

redis.subscribe('hugs');

io.on('connection', function (socket) {
  socket.on('join', function (channel) {
    socket.join(channel);
  });
});

http.listen(process.env.IO_SOCKET, function() {
  fs.chmod(process.env.IO_SOCKET, 0777);
});
