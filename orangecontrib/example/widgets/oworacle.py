from AnyQt.QtWidgets import QComboBox, QTextEdit, QMessageBox, QApplication
from AnyQt.QtGui import QCursor
from AnyQt.QtCore import Qt


from AnyQt.QtWidgets import QLineEdit, QSizePolicy

from Orange.data import Table, ContinuousVariable, DiscreteVariable, StringVariable, TimeVariable
from Orange.data.sql.backend import Backend
from Orange.data.sql.backend.base import Backend, ToSql, BackendError, TableDesc
from Orange.data.sql.table import SqlTable, LARGE_TABLE, AUTO_DL_LIMIT

from Orange.widgets import gui
from Orange.widgets.credentials import CredentialManager
from Orange.widgets.settings import Setting
from Orange.widgets.utils.itemmodels import PyListModel
from Orange.widgets.utils.owbasesql import OWBaseSql
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.widget import Output, Msg, OWWidget
from Orange.widgets.utils.state_summary import format_summary_details


import logging
import re
import warnings
from contextlib import contextmanager
from time import time

#from cx_Oracle import Error, ProgrammingError, SessionPool
import cx_Oracle

#from cx_Oracle.threading import ThreadedConnectionPool

log = logging.getLogger(__name__)

EXTENSIONS = ('tsm_system_time', 'quantile')

#import oraclebackend

MAX_DL_LIMIT = 1000000


def is_oracle(backend):
    return getattr(backend, 'display_name', '') == "Oracle"


class TableModel(PyListModel):
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == Qt.DisplayRole:
            return str(self[row])
        return super().data(index, role)


class BackendModel(PyListModel):
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == Qt.DisplayRole:
            return self[row].display_name
        return super().data(index, role)


class OracleBackend(Backend):
    """Backend for accessing data stored in an Oracle database
    """

    display_name = "Oracle"
    connection_pool = None
    auto_create_extensions = True

    def __init__(self, connection_params):
        super().__init__(connection_params)

        
       # if self.connection_pool is None:
            #self._create_connection_pool()

        #self.missing_extension = []
        #if self.auto_create_extensions:
         #   self._create_extensions()

    def _create_connection_pool(self):
        try:
            #self.connection_pool = SessionPool(
            #    1, 16, **self.connection_params)
            self.connection_pool = cx_Oracle.SessionPool("HO6_ADMIN","HO6_ADMIN","TP-MagS.k1met.loc:1521/XE")
        except Error as ex:
            raise BackendError(str(ex)) from ex

    def _create_extensions(self):
        for ext in EXTENSIONS:
            try:
                query = "CREATE EXTENSION IF NOT EXISTS {}".format(ext)
                with self.execute_sql_query(query):
                    pass
            except BackendError:
                warnings.warn("Database is missing extension {}".format(ext))
                self.missing_extension.append(ext)

    def create_sql_query(self, table_name, fields, filters=(),
                         group_by=None, order_by=None,
                         offset=None, limit=None,
                         use_time_sample=None):
        
        if (len(fields)==1):
            if(fields[0]=="*"):
                sql= ["SELECT", "*", "FROM",table_name]
            else:
                sql = ["SELECT ", fields[0],
                   " FROM", table_name]
        else:
            sql = ["SELECT", ', '.join(fields),
                   "FROM", table_name]
        if use_time_sample is not None:
            sql.append("TABLESAMPLE system_time(%i)" % use_time_sample)
        if filters:
            sql.extend(["WHERE", " AND ".join(filters)])
        if group_by is not None:
            sql.extend(["GROUP BY", ", ".join(group_by)])
        if order_by is not None:
            sql.extend(["ORDER BY", ",".join(order_by)])
        if offset is not None:
            sql.extend(["OFFSET", str(offset)])
        if limit is not None:
            sql.extend(["LIMIT", str(limit)])
       # sql.extend([";"])
        sql.extend(["FETCH","FIRST","500","ROWS","WITH","TIES"])
        query=" ".join(sql)
        #query="".join([query,";"])
        warnings.warn(query)
        return query

    @contextmanager
    def execute_sql_query(self, query, params=None):        
        #if self.connection_pool is None:
        #    self._create_connection_pool()
        connection=cx_Oracle.connect('HO6_ADMIN/HO6_ADMIN@TP-MagS.k1met.loc:1521/XE')
        #connection = self.connection_pool.aquire()
        cur = connection.cursor()
        try:
            #utfquery = cur.mogrify(query, params).decode('utf-8')
            log.debug("Executing: %s", query)
            t = time()
            if (params!=None):
                cur.execute(query, params)
            else:
                cur.execute(query)
            yield cur
            log.info("%.2f ms: %s", 1000 * (time() - t), query)
        except (cx_Oracle.Error, cx_Oracle.ProgrammingError) as ex:
            raise BackendError(str(ex)) from ex
        finally:
            connection.commit()
            #self.connection_pool.release(connection)

    def quote_identifier(self, name):
        return '"%s"' % name

    def unquote_identifier(self, quoted_name):
        if quoted_name.startswith('"'):
            return quoted_name[1:len(quoted_name) - 1]
        else:
            return quoted_name
            

    def list_tables_query(self, schema=None):
        #if schema:
        #    schema_clause = "AND n.nspname = '{}'".format(schema)
        #else:
        #    schema_clause = "AND pg_catalog.pg_table_is_visible(c.oid)"
        #return """SELECT n.nspname as "Schema",
        #                  c.relname AS "Name"
        #               FROM pg_catalog.pg_class c
        #          LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        #              WHERE c.relkind IN ('r','v','m','S','f','')
        #                AND n.nspname <> 'pg_catalog'
        #                AND n.nspname <> 'information_schema'
        #                AND n.nspname !~ '^pg_toast'
        #                {}
        #                AND NOT c.relname LIKE '\\_\\_%'
        #           ORDER BY 1;""".format(schema_clause)
        return "SELECT TABLE_NAME from USER_TABLES ORDER BY TABLE_NAME"

    def list_tables(self, schema=None):
        """Return a list of tables in database

        Parameters
        ----------
        schema : Optional[str]
            If set, only tables from given schema will be listed

        Returns
        -------
        A list of TableDesc objects, describing the tables in the database
        """
        query = self.list_tables_query(schema)
        with self.execute_sql_query(query) as cur:
            tables = []
            for row in cur.fetchall():
                name=row[0]
                sql = name
                tables.append(TableDesc(name, schema, sql))
                log.debug(sql)
            return tables

    def get_fields(self, table_name):
        """Return a list of field names and metadata in the given table

        Parameters
        ----------
        table_name: str

        Returns
        -------
        a list of tuples (field_name, *field_metadata)
        both will be passed to create_variable
        """
        query = self.create_sql_query(table_name, ["*"],order_by=["ISOZEIT"])
        with self.execute_sql_query(query) as cur:
            return cur.description



    def create_variable(self, field_name, field_metadata,
                        type_hints, inspect_table=None):
        if field_name in type_hints:
            var = type_hints[field_name]
        else:
            var = self._guess_variable(field_name, field_metadata,
                                       inspect_table)

        field_name_q = self.quote_identifier(field_name)
        if var.is_continuous:
            if isinstance(var, TimeVariable):
                var.to_sql = ToSql("extract(epoch from {})"
                                   .format(field_name_q))
            else:
                var.to_sql = ToSql("({})::double precision"
                                   .format(field_name_q))
        else:  # discrete or string
            var.to_sql = ToSql("({})::text"
                               .format(field_name_q))
        return var

    def _guess_variable(self, field_name, field_metadata, inspect_table):
        type_code = field_metadata[0]

        FLOATISH_TYPES = (700, 701, 1700)  # real, float8, numeric
        INT_TYPES = (20, 21, 23)  # bigint, int, smallint
        CHAR_TYPES = (25, 1042, 1043,)  # text, char, varchar
        BOOLEAN_TYPES = (16,)  # bool
        DATE_TYPES = (1082, 1114, 1184, )  # date, timestamp, timestamptz
        # time, timestamp, timestamptz, timetz
        TIME_TYPES = (1083, 1114, 1184, 1266,)

        if type_code in FLOATISH_TYPES:
            return ContinuousVariable.make(field_name)

        if type_code in TIME_TYPES + DATE_TYPES:
            tv = TimeVariable.make(field_name)
            tv.have_date |= type_code in DATE_TYPES
            tv.have_time |= type_code in TIME_TYPES
            return tv

        if type_code in INT_TYPES:  # bigint, int, smallint
            if inspect_table:
                values = self.get_distinct_values(field_name, inspect_table)
                if values:
                    return DiscreteVariable.make(field_name, values)
            return ContinuousVariable.make(field_name)

        if type_code in BOOLEAN_TYPES:
            return DiscreteVariable.make(field_name, ['false', 'true'])

        if type_code in CHAR_TYPES:
            if inspect_table:
                values = self.get_distinct_values(field_name, inspect_table)
                # remove trailing spaces
                values = [v.rstrip() for v in values]
                if values:
                    return DiscreteVariable.make(field_name, values)

        return StringVariable.make(field_name)

    def count_approx(self, query):
        #sql = "EXPLAIN " + query
        #with self.execute_sql_query(sql) as cur:
        #    s = ''.join(row[0] for row in cur.fetchall())
        #return int(re.findall(r'rows=(\d*)', s)[0])
        return 500

    def __getstate__(self):
        # Drop connection_pool from state as it cannot be pickled
        state = dict(self.__dict__)
        state.pop('connection_pool', None)
        return state

    def __setstate__(self, state):
        # Create a new connection pool if none exists
        self.__dict__.update(state)
        if self.connection_pool is None:
            self._create_connection_pool()

class OWOracle(OWWidget):
    name = "Oracle Table"
    #id = "orange.widgets.data.oracle"
    description = "Load dataset from Oracle."
    icon = "icons/Oracle.svg"
    priority = 30
    #category = "Data"
    keywords = ["load"]

    class Outputs:
        data = Output("Data", Table, doc="Attribute-valued dataset read from the input file.")


    class Error(OWWidget.Error):
        no_backends = Msg("Please install a backend to use this widget.")

    class Information(OWWidget.Information):
        data_sampled = Msg("Data description was generated from a sample.")

    class Warning(OWWidget.Warning):
        missing_extension = Msg("Database is missing extensions: {}")

    want_main_area = False
    resizing_enabled = False

    host = Setting(None)  # type: Optional[str]
    port = Setting(None)  # type: Optional[str]
    database = Setting(None)  # type: Optional[str]
    schema = Setting(None)  # type: Optional[str]
    username = ""
    password = ""
    settings_version = 2

    #selected_backend = Setting(None)
    table = Setting(None)
    sql = Setting("")
    guess_values = Setting(True)
    download = Setting(False)

    materialize = Setting(False)
    materialize_table_name = Setting("")

    

    def __init__(self):
        # Lint
        self.backends = None
        self.backendcombo = None
        self.tables = None
        self.tablecombo = None
        self.sqltext = None
        self.custom_sql = None
        self.downloadcb = None
        super().__init__()
        self._setup_gui()
       

    def _setup_gui(self):
        #super()._setup_gui()
        #self._add_backend_controls()
        #super().__init__()
        self.backend = None  # type: Optional[Backend]
        self.data_desc_table = None  # type: Optional[Table]
        self.database_desc = None  # type: Optional[OrderedDict]
        self._setup_gui2()
        #self.connect()
        self._add_tables_controls()

    def _setup_gui2(self):
        self.controlArea.setMinimumWidth(360)

        vbox = gui.vBox(self.controlArea, "Server", addSpace=True)
        self.serverbox = gui.vBox(vbox)
        self.servertext = QLineEdit(self.serverbox)
        self.servertext.setPlaceholderText("Server")
        self.servertext.setToolTip("Server")
        self.servertext.editingFinished.connect(self._load_credentials)
        if self.host:
            self.servertext.setText(self.host if not self.port else
                                    "{}:{}".format(self.host, self.port))
        self.serverbox.layout().addWidget(self.servertext)

        self.databasetext = QLineEdit(self.serverbox)
        self.databasetext.setPlaceholderText("Database[/Schema]")
        self.databasetext.setToolTip("Database or optionally Database/Schema")
        if self.database:
            self.databasetext.setText(
                self.database if not self.schema else
                "{}/{}".format(self.database, self.schema))
        self.serverbox.layout().addWidget(self.databasetext)
        self.usernametext = QLineEdit(self.serverbox)
        self.usernametext.setPlaceholderText("Username")
        self.usernametext.setToolTip("Username")

        self.serverbox.layout().addWidget(self.usernametext)
        self.passwordtext = QLineEdit(self.serverbox)
        self.passwordtext.setPlaceholderText("Password")
        self.passwordtext.setToolTip("Password")
        self.passwordtext.setEchoMode(QLineEdit.Password)

        self.serverbox.layout().addWidget(self.passwordtext)

        self._load_credentials()

        self.connectbutton = gui.button(self.serverbox, self, "Connect",
                                        callback=self.connect)
        self.connectbutton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    #def _add_backend_controls(self):
    #    box = self.serverbox
    #    self.backends = BackendModel(Backend.available_backends())
    #    self.backendcombo = QComboBox(box)
    #    if self.backends:
    #        self.backendcombo.setModel(self.backends)
    #        names = [backend.display_name for backend in self.backends]
    #        if self.selected_backend and self.selected_backend in names:
    #            self.backendcombo.setCurrentText(self.selected_backend)
    #    else:
    #        self.Error.no_backends()
    #        box.setEnabled(False)
    #    self.backendcombo.currentTextChanged.connect(self.__backend_changed)
    #    box.layout().insertWidget(0, self.backendcombo)

    #def __backend_changed(self):
    #    backend = self.get_backend()
    #    self.selected_backend = backend.display_name if backend else None

    def _add_tables_controls(self):
        vbox = gui.vBox(self.controlArea, "Tables", addSpace=True)
        box = gui.vBox(vbox)
        self.tables = TableModel()

        self.tablecombo = QComboBox(
            minimumContentsLength=35,
            sizeAdjustPolicy=QComboBox.AdjustToMinimumContentsLength
        )
        self.tablecombo.setModel(self.tables)
        self.tablecombo.setToolTip('table')
        self.tablecombo.activated[int].connect(self.select_table)
        box.layout().addWidget(self.tablecombo)

        self.custom_sql = gui.vBox(box)
        self.custom_sql.setVisible(False)
        self.sqltext = QTextEdit(self.custom_sql)
        self.sqltext.setPlainText(self.sql)
        self.custom_sql.layout().addWidget(self.sqltext)

        mt = gui.hBox(self.custom_sql)
        cb = gui.checkBox(mt, self, 'materialize', 'Materialize to table ')
        cb.setToolTip('Save results of the query in a table')
        le = gui.lineEdit(mt, self, 'materialize_table_name')
        le.setToolTip('Save results of the query in a table')

        gui.button(self.custom_sql, self, 'Execute', callback=self.open_table)

        box.layout().addWidget(self.custom_sql)

        gui.checkBox(box, self, "guess_values",
                     "Auto-discover categorical variables",
                     callback=self.open_table)

        self.downloadcb = gui.checkBox(box, self, "download",
                                       "Download data to local memory",
                                       callback=self.open_table)

    def highlight_error(self, text=""):
        err = ['', 'QLineEdit {border: 2px solid red;}']
        self.servertext.setStyleSheet(err['server' in text or 'host' in text])
        self.usernametext.setStyleSheet(err['role' in text])
        self.databasetext.setStyleSheet(err['database' in text])

    def get_backend(self):
        return OracleBackend

    def open_table(self):
        data = self.get_table()
        self.data_desc_table = data
        self.Outputs.data.send(data)
        info = len(data) if data else self.info.NoOutput
        detail = format_summary_details(data) if data else ""
        self.info.set_output_summary(info, detail)

    def on_connection_success(self):
        #if getattr(self.backend, 'missing_extension', False):
        #    self.Warning.missing_extension(
        #        ", ".join(self.backend.missing_extension))
        #    self.download = True
        #    self.downloadcb.setEnabled(False)
        #if not is_oracle(self.backend):
        #    self.download = True
        #    self.downloadcb.setEnabled(False)
        #self.on_connection_success()
        self.refresh_tables()
        self.select_table()

    def on_connection_error(self, err):
        self.on_connection_error(err)
        self.highlight_error(str(err).split("\n")[0])

    def clear(self):
        
        self.Warning.missing_extension.clear()
        self.downloadcb.setEnabled(True)
        self.highlight_error()
        self.tablecombo.clear()
        self.tablecombo.repaint()

    def refresh_tables(self):
        self.tables.clear()
        if self.backend is None:
            self.data_desc_table = None
            return

        self.tables.append("Select a table")
        self.tables.append("Custom SQL")
        self.tables.extend(self.backend.list_tables(self.schema))
        index = self.tablecombo.findText(str(self.table))
        self.tablecombo.setCurrentIndex(index if index != -1 else 0)
        self.tablecombo.repaint()

    # Called on tablecombo selection change:
    def select_table(self):
        curIdx = self.tablecombo.currentIndex()
        if self.tablecombo.itemText(curIdx) != "Custom SQL":
            self.custom_sql.setVisible(False)
            return self.open_table()
        else:
            self.custom_sql.setVisible(True)
            self.data_desc_table = None
            self.database_desc["Table"] = "(None)"
            self.table = None
            if len(str(self.sql)) > 14:
                return self.open_table()
        return None

    def get_table(self):
        curIdx = self.tablecombo.currentIndex()
        if (not self.database_desc):
            self.database_desc={}
        if curIdx <= 0:
            if self.database_desc:
                self.database_desc["Table"] = "(None)"
            self.data_desc_table = None
            return None

        if self.tablecombo.itemText(curIdx) != "Custom SQL":
            self.table = self.tables[self.tablecombo.currentIndex()]
            #self.database_desc["Table"] = self.table
            #if "Query" in self.database_desc:
            #    del self.database_desc["Query"]
            what = self.table
        else:
            what = self.sql = self.sqltext.toPlainText()
            self.table = "Custom SQL"
            if self.materialize:
                if not self.materialize_table_name:
                    #cx_Oracle.Error.connection(
                    #    "Specify a table name to materialize the query")
                    return None
                try:
                    with self.backend.execute_sql_query("DROP TABLE IF EXISTS " +
                                                        self.materialize_table_name):
                        pass
                    with self.backend.execute_sql_query("CREATE TABLE " +
                                                        self.materialize_table_name +
                                                        " AS " + self.sql):
                        pass
                    with self.backend.execute_sql_query("ANALYZE " + self.materialize_table_name):
                        pass
                except BackendError as ex:
                    #cx_Oracle.Error.connection(str(ex))
                    return None

        try:
            table = SqlTable(dict(host=self.host,
                                  port=self.port,
                                  database=self.database,
                                  user=self.username,
                                  password=self.password),
                             what,
                             backend=type(self.backend),
                             inspect_values=False)
        except BackendError as ex:
            #cx_Oracle.Error.connection(str(ex))
            return None

        #cx_Oracle.Error.connection.clear()

        sample = False

        if table.approx_len() > LARGE_TABLE and self.guess_values:
            confirm = QMessageBox(self)
            confirm.setIcon(QMessageBox.Warning)
            confirm.setText("Attribute discovery might take "
                            "a long time on large tables.\n"
                            "Do you want to auto discover attributes?")
            confirm.addButton("Yes", QMessageBox.YesRole)
            no_button = confirm.addButton("No", QMessageBox.NoRole)
            if is_postgres(self.backend):
                sample_button = confirm.addButton("Yes, on a sample",
                                                  QMessageBox.YesRole)
            confirm.exec()
            if confirm.clickedButton() == no_button:
                self.guess_values = False
            elif is_postgres(self.backend) and \
                    confirm.clickedButton() == sample_button:
                sample = True

        self.Information.clear()
        if self.guess_values:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            if sample:
                s = table.sample_time(1)
                domain = s.get_domain(inspect_values=True)
                self.Information.data_sampled()
            else:
                domain = table.get_domain(inspect_values=True)
            QApplication.restoreOverrideCursor()
            table.domain = domain

        if self.download:
            if table.approx_len() > AUTO_DL_LIMIT:
                if is_postgres(self.backend):
                    confirm = QMessageBox(self)
                    confirm.setIcon(QMessageBox.Warning)
                    confirm.setText("Data appears to be big. Do you really "
                                    "want to download it to local memory?")

                    if table.approx_len() <= MAX_DL_LIMIT:
                        confirm.addButton("Yes", QMessageBox.YesRole)
                    no_button = confirm.addButton("No", QMessageBox.NoRole)
                    sample_button = confirm.addButton("Yes, a sample",
                                                      QMessageBox.YesRole)
                    confirm.exec()
                    if confirm.clickedButton() == no_button:
                        return None
                    elif confirm.clickedButton() == sample_button:
                        table = table.sample_percentage(
                            AUTO_DL_LIMIT / table.approx_len() * 100)
                else:
                    if table.approx_len() > MAX_DL_LIMIT:
                        QMessageBox.warning(
                            self, 'Warning', "Data is too big to download.\n")
                        return None
                    else:
                        confirm = QMessageBox.question(
                            self, 'Question',
                            "Data appears to be big. Do you really "
                            "want to download it to local memory?",
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if confirm == QMessageBox.No:
                            return None

            table.download_data(MAX_DL_LIMIT)
            table = Table(table)

        return table

    @classmethod
    def migrate_settings(cls, settings, version):
        if version < 2:
            # Until Orange version 3.4.4 username and password had been stored
            # in Settings.
            cm = cls._credential_manager(settings["host"], settings["port"])
            cm.username = settings["username"]
            cm.password = settings["password"]

    def _load_credentials(self):
        self._parse_host_port()
        cm = self._credential_manager(self.host, self.port)
        self.username = cm.username
        self.password = cm.password

        if self.username:
            self.usernametext.setText(self.username)
        if self.password:
            self.passwordtext.setText(self.password)

    def _save_credentials(self):
        cm = self._credential_manager(self.host, self.port)
        cm.username = self.username or ""
        cm.password = self.password or ""

    @staticmethod
    def _credential_manager(host, port):
        return CredentialManager("SQL Table: {}:{}".format(host, port))

    def _parse_host_port(self):
        hostport = self.servertext.text().split(":")
        self.host = hostport[0]
        self.port = hostport[1] if len(hostport) == 2 else None

    def _check_db_settings(self):
        self._parse_host_port()
        self.database, _, self.schema = self.databasetext.text().partition("/")
        self.username = self.usernametext.text() or None
        self.password = self.passwordtext.text() or None

    def connect(self):
        self.clear()
        self._check_db_settings()
        if not self.host or not self.database:
            return
        try:
            backend = self.get_backend()
            if backend is None:
                return
            self.backend = backend(dict(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            ))
            self.on_connection_success()
        except BackendError as err:
            self.on_connection_error(err)

    def send_report(self):
        if not self.database_desc:
            self.report_paragraph("No database connection.")
            return
        self.report_items("Database", self.database_desc)
        if self.data_desc_table:
            self.report_items("Data",
                              report.describe_data(self.data_desc_table))


if __name__ == "__main__":  # pragma: no cover
    WidgetPreview(OWOracle).run()
