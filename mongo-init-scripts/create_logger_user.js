db = db.getSiblingDB("logs");

db.createUser({
    user: "logger",
    pwd: "logger_pass",
    roles: [{ role: "readWrite", db: "logs" }]
});