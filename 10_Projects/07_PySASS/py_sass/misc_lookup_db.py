import os
import sqlite3
import datetime
import typing
import gzip

from . import _config as sp
from ._tt_instruction import TT_Instruction
from .sass_class import SASS_Class
from .sm_cu_props import SM_Cu_Props
from .sass_class_props import SASS_Class_Props
from .sm_cu import SM_XX_Instr_Desc

class LookupDB:
    def __init__(self):
        t_location = os.path.dirname(os.path.realpath(__file__))
        tt = datetime.datetime.now()
        db_name = "lookup.db"

        self.__pp = "{0}/DocumentSASS/{1}".format(t_location, db_name)
        self.__db_con = sqlite3.Connection(self.__pp)
        self.__db_name = db_name

    @property
    def pp(self) -> str: return self.__pp
    @property
    def db_con(self) -> sqlite3.Connection: return self.__db_con
    @property
    def db_name(self) -> str: return self.__db_name

    def get_serialized(self) -> bytes: return gzip.compress(self.__db_con.serialize())

    def create(self, props_list:typing.List[typing.Dict]):
        if os.path.exists(self.__pp):
            os.remove(self.__pp)
            self.__db_con = sqlite3.Connection(self.__pp)

        stmt1 = """
        CREATE TABLE Search (
            SearchId integer PRIMARY KEY autoincrement,
            SmId Integer not null,
            ClassName Text not null,
            Opcode Text not null,
            Description Text,
            Format Text not null,
            CreatedTS DEFAULT CURRENT_TIMESTAMP
        );
        """

        # info_rows = [sp.CONST_NAME__FORMAT, sp.CONST_NAME__CONDITIONS, sp.CONST_NAME__PROPERTIES, sp.CONST_NAME__PREDICATES, sp.CONST_NAME__OPCODES, sp.CONST_NAME__ENCODING]

        # stmt2 = f"""
        # CREATE TABLE Info (
        #     InfoId integer PRIMARY KEY autoincrement,
        #     SearchId integer not null,
        #     {",\n".join("{0} Text not null".format(r) for r in info_rows)}
        #     ,FOREIGN KEY(SearchId) REFERENCES Search(SearchId)
        # );
        # """

        stmt3 = f"""
        CREATE TABLE Enum (
            EnumId integer PRIMARY KEY autoincrement,
            Name Text not null,
            Value Text not null,
            UNIQUE(Name, Value)
        );
        """

        stmt4 = f"""
        CREATE TABLE Props (
            PropsId integer PRIMARY KEY autoincrement,
            SearchId integer not null,
            EnumId integer not null,
            FOREIGN KEY(SearchId) REFERENCES Search(SearchId),
            FOREIGN KEY(EnumId) REFERENCES Enum(EnumId)
        );
        """

        stmt5 = f"""
        INSERT INTO Enum (Name, Value) VALUES
        {','.join(['\n("{0}", "{1}")'.format(x['p'], x['n']) for x in props_list])};
        """

        self.run_stmt(stmt1)
        # self.run_stmt(stmt2)
        self.run_stmt(stmt3)
        self.run_stmt(stmt4)
        self.run_stmt(stmt5)
        self.__db_con.commit()


    def run_stmt(self, stmt, commit_after=True):
        cursor:sqlite3.Cursor = self.__db_con.cursor()
        res = None
        try:
            res = cursor.execute(stmt)
        except sqlite3.Error as error:
            self.__db_con.rollback()
            self.__db_con.close()
            print(error.args)
            raise Exception("DB exec failed for stmt: [{0}]!".format(stmt))
        if commit_after: self.__db_con.commit()
        return res

    def run_stmt2(self, stmt:str, args:tuple, commit_after=True):
        cursor:sqlite3.Cursor = self.__db_con.cursor()
        res = None
        try:
            res = cursor.execute(stmt, args)
        except sqlite3.Error as error:
            self.__db_con.rollback()
            self.__db_con.close()
            print(error.args)
            raise Exception("DB exec failed for stmt: [{0}]!".format(stmt))
        if commit_after: self.__db_con.commit()
        return res
    
    def insert_sm_categories(self, categories:set):
        stmt1 = f"""SELECT DISTINCT Value from Enum where Name = 'Category'"""
        res:sqlite3.Cursor = self.run_stmt(stmt1)
        resl = res.fetchall()
        ress = {x[0] for x in resl}

        diff = categories.difference(ress)
        if diff:
            stmt2 = f"""
            INSERT INTO Enum (Name, Value) VALUES
            {','.join(['\n("{0}", "{1}")'.format('Category', x) for x in categories.difference(ress)])};
            """

            self.run_stmt(stmt2)

    def insert_class(self, sm_nr:int, props:SM_Cu_Props, c_desc:SM_XX_Instr_Desc|None, sass_class:SASS_Class, props_list:typing.List[typing.Dict]):
        c_props:SASS_Class_Props = sass_class.props

        SmNr:int = sm_nr
        ClassName:str = sass_class.class_name
        Opcode:str = c_props.opcode
        Description:str = c_desc.desc if c_desc is not None else ''
        format_tt:TT_Instruction = sass_class.FORMAT
        Format:str = format_tt.to_other_kind_of_string(c_props.opcode)

        istmt1 = f"""INSERT INTO Search (SmId, ClassName, Opcode, Description, Format) VALUES ({SmNr}, "{ClassName}", "{Opcode}", "{Description}", "{Format}");"""

        SearchCursor:sqlite3.Cursor = self.run_stmt(istmt1)
        SearchId:int = SearchCursor.lastrowid

        obj_dict = dict()
        for ll in props_list:
            if ll['o'] == SM_Cu_Props.__name__: 
                obj_dict[SM_Cu_Props.__name__] = props
            elif ll['o'] == SASS_Class_Props.__name__ : 
                obj_dict[SASS_Class_Props.__name__] = c_props
            else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        
        search_stmt = """SELECT EnumId FROM Enum WHERE Name = '{0}' AND Value = '{1}'"""

        p_vals = [(x['t'], x['p'], x['n'], x['f'].__get__(obj_dict[x['o']])) for x in props_list]
        p_res_vals = []
        for p_val in p_vals:
            if p_val[0] == 'cn_set':
                if not isinstance(p_val[-1], set): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                if ClassName in p_val[-1]:
                    res:sqlite3.Cursor = self.run_stmt(search_stmt.format(p_val[1], p_val[2]))
                    p_res_vals.append(res.fetchall()[0][0])
            elif p_val[0] == 'TF':
                if not isinstance(p_val[-1], bool): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                if p_val[-1]:
                    res:sqlite3.Cursor = self.run_stmt(search_stmt.format(p_val[1], p_val[2]))
                    p_res_vals.append(res.fetchall()[0][0])
            else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        if c_desc is not None:
            res:sqlite3.Cursor = self.run_stmt(search_stmt.format('Category', c_desc.category))
            p_res_vals.append(res.fetchall()[0][0])

        istmt1 = f"""INSERT INTO Props (SearchId, EnumId) VALUES {",\n".join(["({0},{1})".format(SearchId, i) for i in p_res_vals])}"""
        self.run_stmt(istmt1)

    
