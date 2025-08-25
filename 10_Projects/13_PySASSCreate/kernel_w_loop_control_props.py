import sys
import os
import termcolor as tc
from py_cubin import SM_CuBin_File
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
from control_props import ControlProps
import _config as sp
import sass_create as sc

class KernelWLoopControlProps(ControlProps):
    """This class contains all misc specifications required for a kernel.
    """

    def __init__(self, kk_sm:KK_SM,
                 min_required_instr_count:int, min_required_reg_count:int,
                 template:str,
                 a_base_ureg:tuple, a_base_offset:int,
                 control_base_ureg:tuple, control_base_offset:int,
                 ui_output_base_ureg:tuple, ui_output_base_offset:int,
                 d_output_base_ureg:tuple, d_output_base_offset:int,
                 ui_input_base_ureg:tuple, ui_input_base_offset:int,
                 d_input_base_ureg:tuple, d_input_base_offset:int,
                 clk_out_1_base_ureg:tuple, clk_out_1_base_offset:int,
                 f_output_base_ureg:tuple, f_output_base_offset:int,
                 f_output_odd_base_ureg:tuple, f_output_odd_base_offset:int,
                 cs2r_clk_reg_start:tuple, 
                 cs2r_clk_reg_init:tuple, 
                 cs2r_clk_reg_prequels:tuple, 
                 cs2r_clk_reg_main_1:tuple, 
                 cs2r_clk_reg_main_2:tuple,
                 cs2r_clk_reg_sequels:tuple,
                 cs2r_clk_reg_end:tuple,
                 increment_output:bool,
                 increment_input_as_well:bool,
                 empty_instr:bool, 
                 loop_count:int, 
                 json_file:str|None = None):
        
        super().__init__(kk_sm, min_required_instr_count, min_required_reg_count, template, empty_instr, json_file)

        if not isinstance(a_base_ureg, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(a_base_offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(control_base_ureg, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(control_base_offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ui_output_base_ureg, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ui_output_base_offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(d_output_base_ureg, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(d_output_base_offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(f_output_base_ureg, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(f_output_base_offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(f_output_odd_base_ureg, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(f_output_odd_base_offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ui_input_base_ureg, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ui_input_base_offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(d_input_base_ureg, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(d_input_base_offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(clk_out_1_base_ureg, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(clk_out_1_base_offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cs2r_clk_reg_start, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cs2r_clk_reg_init, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cs2r_clk_reg_prequels, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cs2r_clk_reg_main_1, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cs2r_clk_reg_main_2, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cs2r_clk_reg_sequels, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cs2r_clk_reg_end, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(increment_output, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(increment_input_as_well, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(loop_count, int): raise Exception(sp.CONST__ERROR_ILLEGAL)


        self.__a_base_ureg:tuple = a_base_ureg
        self.__a_base_offset:int = a_base_offset
        self.__control_base_ureg:tuple = control_base_ureg
        self.__control_base_offset:int = control_base_offset
        self.__ui_output_base_ureg:tuple = ui_output_base_ureg
        self.__ui_output_base_offset:int = ui_output_base_offset
        self.__d_output_base_ureg:tuple = d_output_base_ureg
        self.__d_output_base_offset:int = d_output_base_offset
        self.__f_output_base_ureg:tuple = f_output_base_ureg
        self.__f_output_base_offset:int = f_output_base_offset
        self.__f_output_odd_base_ureg:tuple = f_output_odd_base_ureg
        self.__f_output_odd_base_offset:int = f_output_odd_base_offset
        self.__ui_input_base_ureg:tuple = ui_input_base_ureg
        self.__ui_input_base_offset:int = ui_input_base_offset
        self.__d_input_base_ureg:tuple = d_input_base_ureg
        self.__d_input_base_offset:int = d_input_base_offset
        self.__clk_out_1_base_ureg:tuple = clk_out_1_base_ureg
        self.__clk_out_1_base_offset:int = clk_out_1_base_offset
        self.__cs2r_clk_reg_start:tuple = cs2r_clk_reg_start
        self.__cs2r_clk_reg_init:tuple = cs2r_clk_reg_init
        self.__cs2r_clk_reg_prequels:tuple = cs2r_clk_reg_prequels
        self.__cs2r_clk_reg_main_1:tuple = cs2r_clk_reg_main_1
        self.__cs2r_clk_reg_main_2:tuple = cs2r_clk_reg_main_2
        self.__cs2r_clk_reg_sequels:tuple = cs2r_clk_reg_sequels
        self.__cs2r_clk_reg_end:tuple = cs2r_clk_reg_end
        self.__increment_output:bool = increment_output
        self.__increment_input_as_well:bool = increment_input_as_well
        self.__loop_count:int = loop_count
    
    @property
    def a_base_ureg(self) -> tuple: return self.__a_base_ureg
    @property
    def a_base_offset(self) -> int: return self.__a_base_offset
    @property
    def control_base_ureg(self) -> tuple: return self.__control_base_ureg
    @property
    def control_base_offset(self) -> int: return self.__control_base_offset
    @property
    def ui_output_base_ureg(self) -> tuple: return self.__ui_output_base_ureg
    @property
    def ui_output_base_offset(self) -> int: return self.__ui_output_base_offset
    @property
    def d_output_base_ureg(self) -> tuple: return self.__d_output_base_ureg
    @property
    def d_output_base_offset(self) -> int: return self.__d_output_base_offset
    @property
    def f_output_base_ureg(self) -> tuple: return self.__f_output_base_ureg
    @property
    def f_output_base_offset(self) -> int: return self.__f_output_base_offset
    @property
    def f_output_odd_base_ureg(self) -> tuple: return self.__f_output_odd_base_ureg
    @property
    def f_output_odd_base_offset(self) -> int: return self.__f_output_odd_base_offset
    @property
    def ui_input_base_ureg(self) -> tuple: return self.__ui_input_base_ureg
    @property
    def ui_input_base_offset(self) -> int: return self.__ui_input_base_offset
    @property
    def d_input_base_ureg(self) -> tuple: return self.__d_input_base_ureg
    @property
    def d_input_base_offset(self) -> int: return self.__d_input_base_offset
    @property
    def clk_out_1_base_ureg(self) -> tuple: return self.__clk_out_1_base_ureg
    @property
    def clk_out_1_base_offset(self) -> int: return self.__clk_out_1_base_offset
    @property
    def cs2r_clk_reg_start(self) -> tuple: return self.__cs2r_clk_reg_start
    @property
    def cs2r_clk_reg_init(self) -> tuple: return self.__cs2r_clk_reg_init
    @property
    def cs2r_clk_reg_prequels(self) -> tuple: return self.__cs2r_clk_reg_prequels
    @property
    def cs2r_clk_reg_main_1(self) -> tuple: return self.__cs2r_clk_reg_main_1
    @property
    def cs2r_clk_reg_main_2(self) -> tuple: return self.__cs2r_clk_reg_main_2
    @property
    def cs2r_clk_reg_sequels(self) -> tuple: return self.__cs2r_clk_reg_sequels
    @property
    def cs2r_clk_reg_end(self) -> tuple: return self.__cs2r_clk_reg_end
    @property
    def increment_output(self) -> bool: return self.__increment_output
    @property
    def increment_input_as_well(self) -> bool: return self.__increment_input_as_well
    @property
    def loop_count(self) -> int: return self.__loop_count
