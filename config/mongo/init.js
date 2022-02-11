conn = new Mongo();
db = conn.getDB("dynap");
db.createCollection("jobs");
db.createCollection("clients");
