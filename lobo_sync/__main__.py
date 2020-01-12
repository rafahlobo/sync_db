from .sync import Sync
from .config import ORIGIN_DB_CONFIG,TARGET_DB_CONFIG,TABLES


s = Sync(ORIGIN_DB_CONFIG,TARGET_DB_CONFIG,TABLES)
s.run()