# Information of db origin
ORIGIN_DB_CONFIG = {
    "host" : "177.85.96.154",
    "user" : "slsoluti_root",
    "password" : "!Lobo@1212",
    "port" : "3306",
    "database" : "slsoluti_replication"
}

# Information of db target
TARGET_DB_CONFIG = {
    "host" : "127.0.0.1",
    "user" : "root",
    "password" : "",
    "port" : "3307",
    "database" : "replication"
}

# Tables to replication
TABLES = ["user","price"]