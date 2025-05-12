// init.js
use lesBellesMiches;

db.createCollection("user");
db.createCollection("message");

db.user.insertMany([
    {
        username: "alice",
        password: Binary.createFromBase64("JDJiJDEwJEpIOVUwbWxZZE9aVW4xWWgxSzI3Wk9EMXhFWTdEU28wVS5tUFpzdlN2bXhibjBJS0Z1ajRh", 0)
    },
    {
        username: "bob",
        password: Binary.createFromBase64("JDJiJDEwJkMyQkRScnN4ZXkyUkp1VGtWV2MwLmVUeTZVMURvRFhHQ0xFcUREUlJwcG4ydXo0VnBGRWJD", 0)
    }
]);


db.message.insertOne({
    sender: "alice",
    recipient: "bob",
    text: "Hello Bob!",
    timestamp: new Date(),
    read: false
});