import mysql.connector
import datetime


# from mysql.connector import errors


class Mysql_dao():
    # Conexão ao banco de dados.
    _con = None
    _logger = None

    def setLogger(self, logger):
        Mysql_dao._logger = logger

    def _writeLog(self, msg):
        """ Usado apenas para registrar erros."""
        if Mysql_dao._logger is not None:
            Mysql_dao._logger.error("[Mysql_dao] " + msg)

    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs

    def execute(self, sql, param=None, select=False):
        """ Executa query. """
        try:
            # Obtem conexão ao banco de dados.
            con = self.connect()
            cur = con.cursor()
            cur.execute(sql, param)

        except (mysql.connector.ProgrammingError) as e :
            return False
        except (mysql.connector.DatabaseError, mysql.connector.errors.OperationalError, NotPossibleConnectionException,
                Exception) as e:
            print("## <ERROR> ###")
            print(type(e))
            print(e)
            print(sql)
            print(param)
            print("## </ERROR> ###")
            if select:
                return []
            return False
        if select:
            dados = []
            for reg in cur.fetchall():
                dados.append(self._dict_factory(cursor=cur, row=reg))
        else:
            dados = True
            try:
                con.commit()
            except mysql.connector.errors.OperationalError as e:
                self._writeLog(e)
                dados = False
        self.close(con)
        return dados

    def connect(self):
        try:
            self._kwargs.update({"auth_plugin":"mysql_native_password"})
            return mysql.connector.connect(*self._args, **self._kwargs)
        except mysql.connector.InterfaceError as e:
            raise NotPossibleConnectionException(e)

    def close(self, con):
        """ Finaliza conexão com o banco de dados."""
        con.close()

    ''' Converte para dicionário '''

    def _dict_factory(self, cursor, row):
        # print(cursor.description)
        dicionario = {}
        for item in enumerate(cursor.column_names):
            dicionario[item[1]] = row[item[0]]
        return dicionario

    ''' Agora '''

    def _now(self):
        return datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')


class NotPossibleConnectionException(Exception):
    """ Não foi possível conectar ou obter instância do mysql/pool."""
    pass