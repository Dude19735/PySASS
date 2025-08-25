from __future__ import annotations
import sqlite3
import termcolor
from . import _config as sp

class DbTable:
    ColName_TypeId = 'TypeId'
    TableName_SelfParent = 'SelfParent'

    # stmt that returns [('',)] if the table does not exist or
    # all column names complete with their types if it does exist
    # NOTE: don't change the comma separator ',' to ', ' => will make a split stmt later on not work as intended
    Stmt_Exists = """
    SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM sqlite_schema WHERE type='table' AND name='{table_name}') 
        THEN (SELECT group_concat(name || ' ' || type, ',') FROM pragma_table_info('{table_name}')) 
        ELSE '' 
    END AS result;
"""

    def __init__(self, tObj:object, parent_table_name:str|None, col_names_t:list, db_con:sqlite3.Connection, self_parent:bool=False):
        if not isinstance(tObj, object): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(parent_table_name, str|None): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(col_names_t, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(db_con, sqlite3.Connection): raise Exception(sp.CONST__ERROR_ILLEGAL)

        self.__db_con = db_con
        self.__table_name = DbTable.get_table_name(tObj)
        # We have one instance where one table is it's own parent.
        # In this case, we need to circumvent the system where the main id is also the parent id because
        # like that, the table would need two [TableName]Id columns
        # We call the new column SelfParentId
        self.__self_parent = self_parent

        if parent_table_name is not None and parent_table_name.startswith('Db_'): self.__parent_table_name = DbTable.get_table_name_t(parent_table_name)
        else: self.__parent_table_name = parent_table_name

        # Make sure we never miss any self-parenting cases
        if not self_parent and self.__parent_table_name == self.__table_name:
            raise Exception(sp.CONST__ERROR_ILLEGAL)

        exist_stmt = DbTable.Stmt_Exists.format(table_name=self.__table_name)
        rn,r = self.exec_stmt(self.__db_con, exist_stmt, is_insert=False) # type: ignore
        cols = r[0]
        if cols != ('',): 
            col_names_t = cols[0].split(',')
            self.__exists = True
            
            # If we exist, recover all index columns
            self.__id = col_names_t[0].split()[0]
            #  => make sure that col 0 is the Id and is table_name + 'Id'
            if self.__id != self.__table_name + "Id": raise Exception(sp.CONST__ERROR_UNEXPECTED)

            if self.__parent_table_name: 
                self.__parent_id = col_names_t[1].split()[0]
                if self.__table_name != self.__parent_table_name:
                    # If we have a distinct parent table (no self-parenting case in action)
                    #  => make sure that col 1 is the parent Id and is table_name + 'Id'
                    if not self.__parent_id == self.__parent_table_name + 'Id': raise Exception(sp.CONST__ERROR_ILLEGAL)
                elif self.__parent_id == self.__parent_table_name + 'Id': raise Exception(sp.CONST__ERROR_ILLEGAL)
            else: self.__parent_id = ''
            if self.__self_parent: 
                self.__self_parent_id = col_names_t[2].split()[0]
                #  => make sure that col 2 is the self-parenting id and is SelfParentId
                if not self.__self_parent_id == DbTable.TableName_SelfParent + 'Id': raise Exception(sp.CONST__ERROR_ILLEGAL)
            else: self.__self_parent_id = ''

            # Cut the relevant part of the columns:
            #  => if we have a self-parenting id, omit the first three columns
            #  => if we have a regular parenting situation, omit the first two rows
            #  => otherwise just omit the firt column that is the main id
            #  => always omit the last column that contains the automatically set CreatedTS
            if self.__parent_id:
                if self.__self_parent_id: self.__col_names_t = col_names_t[3:-1]
                else: self.__col_names_t = col_names_t[2:-1]
            else: self.__col_names_t = col_names_t[1:-1]
        else: 
            # If we don't exist yet, we will never have a self referenced table
            #  => no need for exceptional behaviour with the self_parent_id
            #  => simply add one additional row SelfParentId if we need self-parenting capability
            self.__exists = False
            self.__id = self.__table_name + 'Id'
            self.__col_names_t = col_names_t
            if self.__parent_table_name: self.__parent_id = self.__parent_table_name + 'Id'
            else: self.__parent_id = ''
            if self.__self_parent: self.__self_parent_id = DbTable.TableName_SelfParent + 'Id'
            else: self.__self_parent_id = ''

        # all_cols_t will be the columns to replace for the insert_stmt. It needs the parent_id and self_parent_id columns
        # but not the main id field
        # Make sure that all_cols_t is a copy of self.__col_names_t and not a reference!
        all_cols_t = self.__col_names_t
        if self.__self_parent_id: all_cols_t = [self.__self_parent_id + " integer"] + all_cols_t
        if self.__parent_id: all_cols_t = [self.__parent_id + " integer"] + all_cols_t
        
        self.__col_names, self.__insert_stmt, self.__insert_stmt_np = DbTable.args_and_params(self.__table_name, all_cols_t)

    @property
    def table_name(self) -> str: return self.__table_name
    @property
    def parent_table_name(self) -> str|None: return self.__parent_table_name
    @property
    def is_self_parenting(self) -> bool: return self.__self_parent
    @property
    def parent_id(self) -> str: return self.__parent_id
    @property
    def self_parent_id(self) -> str: return self.__self_parent_id

    def create_if_not_exists(self):
        if self.__exists:
            # The table already exists => return correct parent id field
            #  => if we have a self-parenting case, return SelfParentId
            if self.__table_name == self.__parent_table_name:
                # This can never happen, if we don't have a self-parenting case because only in the self-parenting case, the table name
                # is the same as the parent table name
                if self.__self_parent_id == '': raise Exception(sp.CONST__ERROR_UNEXPECTED)
                return self, self.__self_parent_id
            #  => otherwise return the real parent id
            else: return self, self.__parent_id

        # Create foreign key references and arrange them properly for the create stmt
        parent_id_fk = self.get_fks(self.__parent_id)
        self_parent_id_fk = self.get_fks(self.__self_parent_id)
        fks = ''
        if parent_id_fk: fks += ',' + parent_id_fk
        if self_parent_id_fk: fks += ',' + self_parent_id_fk

        # Create the parent and self parent id stuff and arrange them properly for the create stmt
        if self.__parent_id: parent_id = self.__parent_id + " integer, "
        else: parent_id = ''
        if self.__self_parent_id: self_parent_id = self.__self_parent_id + " integer, "
        else: self_parent_id = ''

        cols = ",".join(self.__col_names_t)
        stmt = """CREATE TABLE {table_name} (
                    {id} integer PRIMARY KEY autoincrement,
                    {parent_id}{self_parent_id}
                    {cols},
                    CreatedTS DEFAULT CURRENT_TIMESTAMP
                    {fks}
                    );""".format(table_name=self.__table_name, id=self.__id, parent_id=parent_id,self_parent_id=self_parent_id, cols=cols, fks=fks)
        self.exec_stmt(self.__db_con, stmt)

        return self, self.__parent_id

    def get_fks(self, id_field):
        if id_field == '': return ''
        return 'FOREIGN KEY(' + id_field + ') REFERENCES ' + id_field[:-2] + '(' + id_field + ')'

    def insert(self, **args):
        stmt = self.__insert_stmt
        return self.exec_stmt(self.__db_con, stmt=stmt.format(**args), is_insert=True)

    def insert_np(self, args:tuple):
        stmt = self.__insert_stmt_np
        return self.exec_stmt(self.__db_con, stmt=(stmt, args), is_insert=True)

    def select(self, conditions:str='', order_by:str=''):
        stmt = """SELECT * FROM {table_name}""".format(table_name=self.__table_name)
        if conditions: stmt += """ WHERE {conditions}""".format(conditions=conditions)
        if order_by: stmt += """ ORDER BY {order_by}""".format(order_by=order_by)
        stmt += ';'
        return self.exec_stmt(self.__db_con, stmt)

    def exec_stmt(self, db_con:sqlite3.Connection, stmt:str|tuple, is_insert=False, commit_on_finish=False):
        cursor:sqlite3.Cursor = db_con.cursor()
        res = None
        try:
            if isinstance(stmt, tuple):
                # This one is used if we have to insert byte data into the data base.
                # If we use named stmt (.format(...)) then the binary b'...' will be obfuscated by a conversion
                # to string and the insert will fail because we insert garbage into a blob.
                # NOTE: that the sequence of the insert fields must be the same as the sequence in the data base
                res = cursor.execute(stmt[0], stmt[1])
            else:
                res = cursor.execute(stmt)
        except sqlite3.Error as error:
            db_con.rollback()
            db_con.close()
            msg = "[{0}]: {1}".format(termcolor.colored("ERROR", 'red', attrs=['bold']), error.args[0])
            print(msg)
            raise Exception(msg)
        
        # NOTE: commiting after a stmt has an enormous, negative impact on performance!
        #       Do not commit after every single stmt if many stmts have to be performed!
        if commit_on_finish: db_con.commit()
        
        if is_insert: return res.lastrowid
        if res.description:
            row_names = [i[0] for i in res.description]
            rows = list(res)
        else:
            row_names = []
            rows = []
        return row_names, rows

    @staticmethod
    def args_and_params(table_name:str, t_col_names:list):
        if not isinstance(table_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(t_col_names, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        col_names = [c.split()[0] for c in t_col_names]
        args = "({0})".format(", ".join(col_names))
        params = "({0})".format(", ".join("'{{{0}}}'".format(c[0]) if c[1].lower() == 'text' else "{{{0}}}".format(c[0]) for c in [[cc for cc in c.split()] for c in t_col_names]))
        insert_stmt = """INSERT INTO {table_name} {args} VALUES {params};""".format(table_name=table_name, args=args, params=params)
        insert_stmt_np = """INSERT INTO {table_name} {args} VALUES ({params});""".format(table_name=table_name, args=args, params=",".join(len(t_col_names)*'?'))
        return col_names, insert_stmt, insert_stmt_np

    @staticmethod
    def translate_type(type_name:str):
        if type_name == 'int': return 'integer'
        if type_name == 'str': return 'text'
        if type_name == 'bytes': return 'blob'
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

    @staticmethod
    def get_table_name_t(proxy_name:str):
        return proxy_name.lstrip('Db').rstrip('Proxy')[1:-1]

    @staticmethod
    def get_table_name(obj:object):
        return DbTable.get_table_name_t(type(obj).__name__)

    @staticmethod
    def get_insert_args(obj:object, tb:DbTable, types:dict, pid:str|None=None, parent_id:int|None=None, refs:dict=dict()):
        if not isinstance(tb, DbTable): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(types, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(pid, str|None): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(parent_id, int|None): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(refs, dict|None): raise Exception(sp.CONST__ERROR_ILLEGAL)

        table_name = tb.table_name

        args = {i[6:-3]:getattr(obj, i) for i in dir(obj) if i[4].isnumeric()}
        type_id = getattr(obj, '___0X_Type___', False)
        if type_id is not False:
            args = {DbTable.ColName_TypeId:types[table_name][type_id]} | args
        if pid is not None:
            if tb.is_self_parenting:
                if pid == tb.parent_id:
                    # Potential self-parenting but with regular parent.
                    # Assign the parent to the regular parent_id spot.
                    args = {tb.parent_id:parent_id, tb.self_parent_id:'NULL'} | args
                else:
                    # Self-parenting in action: assign the parent_id to the self-parenting id, not the regular
                    # parent id.
                    # NOTE: not doing wo will result in a UNIQUE constraint violation
                    args = {tb.parent_id:'NULL', tb.self_parent_id:parent_id} | args    
            else:
                args = {pid:parent_id} | args
        if refs: args |= refs
        return args

    @staticmethod
    def get_col_names(obj:object, parent_table_name:str=''):
        # All arguments with ___...___ represent db fields => read all of them
        t_names = [i for i in dir(obj) if i.startswith('___') and i.endswith('___')]
        
        # If we reference a Type, we have an entry with ___0X_Type___ amongst them
        type_id = [t[6:-3]+'Id integer' for t in t_names if t[3:5]=='0X']
        
        # If we have references, we have fields with ___RR_
        refs = [(getattr(obj,i), int(i[5])) for i in t_names if i[3:5]=='RR']
        refs = sorted(refs, key=lambda x:x[1])
        # Create column names for the references (we need them in any case)
        ref_id = ["Ref{0}_{1}Id integer".format(nr, DbTable.get_table_name_t(i.__name__) if isinstance(i,type) else DbTable.get_table_name(i)) for i,nr in refs]
        # If we have a type somewhere, use 'NULL' as value otherwise use the persisted id
        # NOTE: only objects that have been written to db have a persist_id. If we pass a type as ref, it means that 
        #       we have an exception to the rule where an object usually has a reference but doesn't in this specific case
        refs = {i.split()[0]:('NULL' if isinstance(v,type) else v.persist_id) for i,(v,nr) in zip(ref_id, refs)}
        
        # Create a parent_id field with the name of the parent table if we have a parent
        # NOTE: most tables have a parent
        parent_id = [DbTable.get_table_name_t(parent_table_name) + 'Id'] if parent_table_name else []
        
        # Create the remaining colums with column_name and type. These are all the ___01_...___ etc fields. The type is translated from
        # Python int|str|bytes to db.
        t_col_names = parent_id + type_id + ["{0} {1}".format(i[6:-3], DbTable.translate_type(type(getattr(obj,i)).__name__)) for i in t_names if i[3:5].isnumeric()]
        t_col_names.extend(ref_id)

        # Get the linked objects in a list
        # NOTE: a linked object is not persisted yet. It has a parent-child relationship with the current object
        # NOTE: a ref object must already be persisted in the db. It is added with it's Id on the db line for the current object
        links = [getattr(obj,i) for i in t_names if i[3] == 'L']
        return t_col_names, links, refs
