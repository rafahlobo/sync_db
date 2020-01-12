import json
import os

# Information of db origin
ORIGIN_DB_CONFIG = json.loads(os.environ.get("origin_db")) 

# Information of db target
TARGET_DB_CONFIG = json.loads(os.environ.get("target_db")) 

# Tables to replication
TABLES = ["user","price"]