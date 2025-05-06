// init.js
use lesBellesMiches;

db.createCollection("user");
db.createCollection("message");

db.user.insertMany([
    {
        username: "alice",
        // hash de "alice" avec bcrypt (ex: saltRounds=10)
        password: "$2b$10$JH9U0mlYdOZUn1Yh1K27ZOD1xEY7DSo0U.mPZsvSvmxbn0IKFuj4a"
    },
    {
        username: "bob",
        // hash de "bob"
        password: "$2b$10$C2BDRrsxey2RJuTkVWc0.eTy6U1DoDXGCLEqDTRRppn2uz4VpFEbC"
    }
]);

db.message.insertOne({
    sender: "alice",
    recipient: "bob",
    text: "Hello Bob!",
    timestamp: new Date(),
    read: false
});