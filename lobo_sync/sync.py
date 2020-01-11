from .db.mysql_dao import Mysql_dao


class Sync():
    def __init__(self, db_origin, db_target, tables):
        self._db_origin = Mysql_dao(**db_origin)
        self._db_target = Mysql_dao(**db_target)
        self._tables = tables

    def _get_data_table(self, db="origin"):
        """
        Gets all data from the specified tables.
        :param db: string - Only "origin" or "target":
        :return:
        """
        if db not in ("origin", "target"):
            raise Exception("db argument can only contain the values \"origin\" or \"target\". ")
        data = {}
        for table in self._tables:
            query = "select * from %s ;" % (table,)
            data[table] = self._db_origin.execute(sql=query, select=True) \
                if db == "origin" \
                else self._db_target.execute(sql=query, select=True)
        return data

    def _get_struct_to_create_table(self, table_name):
        """
        Returns sql of creation of missing table.
        :param table_name string - Name of table that not found:
        :return: string
        """
        query = "show create table %s " % (table_name,)
        data = self._db_origin.execute(sql=query, select=True)
        return data[0]['Create Table']

    def run(self):
        # Get data of origin
        data_origin = self._get_data_table("origin")
        # Get data of target
        data_target = self._get_data_table("target")

        # Verifies that the target database has all the necessary tables, if not creates them.
        for table in data_target:
            if table is False:
                if self._db_target.execute(self._get_struct_to_create_table(table)):
                    print("Table %s has been created !" % (table,) )
                else:
                    raise Exception("There was an error creating table structure.")


