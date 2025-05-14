// init.js
use lesBellesMiches;

// Supprime les collections si elles existent déjà
db.user.drop();
db.message.drop();

db.createCollection("user");
db.createCollection("message");