from .db.mysql_dao import Mysql_dao
from json import dumps


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
            raise Exception(
                "db argument can only contain the values \"origin\" or \"target\". ")
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

    def check_if_need_reload_data_target(self, table_name, data_origin, data_target):
        value_target = data_target[table_name]
        value_origin = data_origin[table_name]
        if value_target is False and value_origin is not False:
            if self._db_target.execute(self._get_struct_to_create_table(table_name)):
                print("Table %s has been created !" % (table_name,))
                return True
            else:
                raise Exception("There was an error creating table structure.")

        return False

    def _analyzes_if_data_eguals(self, dict1, dict2):
        return dict1 == dict2

    def analyzes_if_data_change(self, origin_data, origin_target, pk_name, table_name):
        """
        returns a list of records where differences were found.
        :return List
        """
        diff = []
        for registry in origin_data:
            registry_target = self._search_key_into_dict(
                pk_name, registry[pk_name], origin_target)
            if registry_target is None:
                diff.append({
                    "action": "insert",
                    "pk_name": pk_name,
                    "table_name": table_name,
                    "registry": registry,
                })
                continue
            if not self._analyzes_if_data_eguals(registry, registry_target):
                diff.append({
                    "action": "update",
                    "pk_name": pk_name,
                    "table_name": table_name,
                    "registry": registry,
                })
        return diff

    def search_registry_to_del(self, origin_data, origin_target, pk_name, table_name):

        diff = []
        for registry in origin_target:
            registry_origin = self._search_key_into_dict(
                pk_name, registry[pk_name], origin_data)
            if registry_origin is None:
                diff.append({
                    "action": "delete",
                    "pk_name": pk_name,
                    "table_name": table_name,
                    "registry": registry,
                })
                
        return diff

    def _search_key_into_dict(self, pk, value, list_data):
        for item in list_data:
            if item[pk] == value:
                return item
        return None

    def get_primary_key_info(self, table_name):
        sql = "SHOW KEYS FROM %s WHERE Key_name = 'PRIMARY'" % table_name
        pk_info = self._db_origin.execute(sql, select=True)
        return pk_info[0]['Column_name']

    def insert_target_registry(self, metadata):

        fields = list(map(lambda key: key, metadata['registry']))
        datas = list(
            map(lambda key: f"'{metadata['registry'][key]}'", metadata['registry']))

        sql = f'insert into {metadata["table_name"]} ({",".join(fields)}) values ({",".join(datas)});'
        return (
            metadata['table_name'],
            metadata['pk_name'],
            metadata['registry'][metadata['pk_name']],
            self._db_target.execute(sql)
        )

    def update_target_registry(self, metadata):
        pk_value = metadata['registry'][metadata['pk_name']]
        del metadata['registry'][metadata['pk_name']]

        datas = list(
            map(lambda key: f"{key}='{metadata['registry'][key]}'", metadata['registry']))

        sql = f'update {metadata["table_name"]} set {",".join(datas)} where {metadata["pk_name"]} = {pk_value}; '
        return (
            metadata['table_name'],
            metadata['pk_name'],
            pk_value,
            self._db_target.execute(sql)
        )

    def delete_target_registry(self, metadata):
        pk_value = metadata['registry'][metadata['pk_name']]
        sql = f'delete from {metadata["table_name"]} where {metadata["pk_name"]} = {pk_value};'
        return (
            metadata['table_name'],
            metadata['pk_name'],
            metadata['registry'][metadata['pk_name']],
            self._db_target.execute(sql)
        )

    def run(self):
        # Get data of origin
        data_origin = self._get_data_table("origin")
        # Get data of target
        data_target = self._get_data_table("target")

        # Verifies that the target database has all the necessary tables, if not creates them.
        for table_name in data_target:
            if self.check_if_need_reload_data_target(table_name, data_origin, data_target):
                data_target = self._get_data_table("target")

        for table_name in data_target:
            registry_o = data_origin[table_name]
            registry_t = data_target[table_name]
            if not registry_o:
                continue
            pk_column_name = self.get_primary_key_info(table_name)

            conflict_list = self.analyzes_if_data_change(
                registry_o, registry_t, pk_column_name, table_name)

            inserts = list(
                filter(lambda x: x['action'] == "insert", conflict_list))
            updates = list(
                filter(lambda x: x['action'] == "update", conflict_list))

            delete = self.search_registry_to_del(
                registry_o, registry_t, pk_column_name, table_name)

            # Synchronize database
            a = map(self.insert_target_registry, inserts)
            print(list(a))
            b = map(self.update_target_registry, updates)
            print(list(b))
            c = map(self.delete_target_registry, delete)
            print(list(c))
