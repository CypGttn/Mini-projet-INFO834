// init.js
use lesBellesMiches;

db.createCollection("user");
db.createCollection("message");

db.user.insertMany([
    { username: "alice", password: "alice" },
    { username: "bob", password: "bob" }
]);
/*
db.message.insertOne({
    sender: "alice",
    recipient: "bob",
    text: "Hello Bob!",
    timestamp: new Date(),
    read: false
});
*/