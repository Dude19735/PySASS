from ._sass_parser_arch import SASS_Parser_Arch
from ._sass_parser_constants import SASS_Parser_Constants
from ._sass_parser_funit import SASS_Parser_Funit
from ._sass_parser_operation import SASS_Parser_Operation
from ._sass_parser_parameters import SASS_Parser_Parameters
from ._sass_parser_registers import SASS_Parser_Registers
from ._sass_parser_tables import SASS_Parser_Tables
from ._sass_func import SASS_Func
from . import _config as sp

"""
This one maps values of the instructions.txt files to objects and dictionaries for easy access.
"""

class SM_Cu_Details:
    NON_FUNC_REG = {'Register','SpecialRegister','Predicate','BarrierRegister','NonZeroRegister', 'NonZeroUniformRegister', 'ZeroUniformRegister'}

    def __init__(self, results:dict, sm_xx:str):
        self.SM_XX = sm_xx
        
        self.ARCHITECTURE_DICT = results['ARCHITECTURE']
        self.PARAMETERS_DICT = results['PARAMETERS']
        self.CONSTANTS_DICT = results['CONSTANTS']
        self.REGISTERS_DICT = results['REGISTERS']
        self.TABLES_DICT = results['TABLES']
        self.TABLES_INV_DICT = results['TABLES_INV']
        self.OPERATION_DICT = results['OPERATION']
        self.FUNIT_DICT = results['FUNIT']
        self.FUNCTIONS_DICT = results['FUNCTIONS']
        self.ACCESSORS_DICT = results['ACCESSORS']

        self.ARCHITECTURE = SASS_Parser_Arch(self.ARCHITECTURE_DICT)
        self.PARAMETERS = SASS_Parser_Parameters(self.PARAMETERS_DICT)
        self.CONSTANTS = SASS_Parser_Constants(self.CONSTANTS_DICT)
        self.REGISTERS = SASS_Parser_Registers(self.REGISTERS_DICT)
        self.TABLES = SASS_Parser_Tables(self.TABLES_DICT)
        self.TABLES_INV = SASS_Parser_Tables(self.TABLES_INV_DICT)
        self.OPERATION = SASS_Parser_Operation(self.OPERATION_DICT)
        self.FUNIT = SASS_Parser_Funit(self.FUNIT_DICT)
        self.FUNCTIONS = SASS_Func(self.FUNCTIONS_DICT)
        self.ACCESSORS = SASS_Func(self.ACCESSORS_DICT)

        self.__op_preds:list = self.OPERATION.PREDICATES
        self.__size_predicates = set(i for i in self.__op_preds if i.endswith('_SIZE'))
        self.__other_predicates = set(i for i in self.__op_preds if not i in self.__size_predicates)
        self.__dst_predicates = set(i for i in self.__size_predicates if i.startswith('IDEST'))
        self.__dsr_rf_predicates = set(i for i in self.__dst_predicates if i.find('INDEX_RF')>0)
        self.__src_predicates = set(i for i in self.__size_predicates if i.startswith('ISRC'))
        self.__src_rf_predicates = set(i for i in self.__src_predicates if i.find('INDEX_RF')>0)
        self.__label_predicates = set(i for i in self.__size_predicates if i.startswith('ILABEL'))

        # check
        if len(self.__size_predicates) + len(self.__other_predicates) != len(self.__op_preds): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if len(self.__dst_predicates) + len(self.__src_predicates) + len(self.__label_predicates) != len(self.__size_predicates): raise Exception(sp.CONST__ERROR_UNEXPECTED)

    @property
    def op_preds(self): return self.__op_preds
    @property
    def size_predicates(self): return self.__size_predicates
    @property
    def dst_predicates(self): return self.__dst_predicates
    @property
    def dsr_rf_predicates(self): return self.__dsr_rf_predicates
    @property
    def src_predicates(self): return self.__src_predicates
    @property
    def src_rf_predicates(self): return self.__src_rf_predicates
    @property
    def label_predicates(self): return self.__label_predicates
    @property
    def other_predicates(self): return self.__other_predicates

    def __iter__(self):
        self.__iter = iter([i for i in dir(self) if not i.startswith('_')])
        return self

    def __next__(self):
        return next(self.__iter)
    
    def as_dict(self):
        return {
            'ARCHITECTURE': self.ARCHITECTURE_DICT,
            'PARAMETERS': self.PARAMETERS_DICT,
            'CONSTANTS': self.CONSTANTS_DICT,
            'REGISTERS': self.REGISTERS_DICT,
            'TABLES': self.TABLES_DICT,
            'TABLES_INV': self.TABLES_INV_DICT,
            'OPERATION': self.OPERATION_DICT,
            'FUNIT': self.FUNIT_DICT,
            'FUNCTIONS': self.FUNCTIONS_DICT,
            'ACCESSORS': self.ACCESSORS_DICT
        }
