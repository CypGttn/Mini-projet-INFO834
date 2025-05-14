// init.js
use lesBellesMiches;

// Création des bases seulement si elles n'existent pas
if (!db.getCollectionNames().includes("user") && !db.getCollectionNames().includes("message")) {db.createCollection("user");db.createCollection("message");}

