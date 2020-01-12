
# sync_db

script to synchronize small database tables.


# Configuration

Set your environment variables from your operating system to contain the connection to the source and target database.
```
origin_db = '{\"host\" : \"172.17.0.2\",\"user\" : \"root\",\"password\": \"root\",\"port\" : 3306,\"database\" : \"temp\"}'

target_db = '{\"host\" : \"172.17.0.3\",\"user\" : \"root\",\"password\": \"root\",\"port\" : 3306,\"database\" : \"temp\"}'
```

`` Edit connection information for your databases  ``