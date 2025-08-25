from __future__ import annotations
import typing
import copy
import termcolor as tc
import itertools as itt
from py_sass import SM_SASS
from py_sass_ext import SASS_Bits
from . import _config as sp
from ._instr_cubin_repr import Instr_CuBin_Repr
from ._instr_cubin import Instr_CuBin, CubinDecodeException
from .sm_cubin_kernel import SM_CuBin_Kernel
from .sm_cubin_kernel_ht import SM_CuBin_Kernel_Head, SM_CuBin_Kernel_Tail
from .sm_cubin_lib import SM_CuBin_Lib
from .sm_cubin_elf import SM_Cubin_Elf

class SM_CuBin_Regs:
    def __init__(self, regs_dict:dict):
        for r,v in regs_dict.items():
            vals = itt.chain.from_iterable([("{0}__{1}__{2}".format(r, vk, vvv),(r, vk, vvv)) for vvv in vv] for vk,vv in v.items())
            for s,e in vals:
                setattr(self, s, e)
    # def name_list(self):
    #     return [r for r in dir(target_cubin.valid_regs) if not (r.startswith('__') or r.endswith('__'))]

class SM_Cubin_Unloaded_Cache_Exception(Exception):
    pass

class SM_CuBin_File:
    # This one is a hack to load a new sm in the webservice version of this
    cur_sm_nr:int = 0
    def __init__(self, sass_c:SM_SASS|dict, file_data:str|bytes, wipe=False, selected_kernel='', no_decode=False, verbose=False):
        # We are loading a file for the first time...
        if isinstance(file_data, str) and isinstance(sass_c, SM_SASS):
            self.__init_as_dict = False
            # Regular load from file
            cubin = SM_CuBin_Lib.read_ncod_full(file_data)
            sass = sass_c
            sm_nr:int = sass.sm_nr
            SM_CuBin_File.cur_sm_nr = sm_nr
        elif isinstance(file_data, bytes) and isinstance(sass_c, dict):
            self.__init_as_dict = True
            # Load from just bytes (used in the webservice version)
            cubin = SM_CuBin_Lib.read_ncod_full_b(file_data, "Web/FromBin")
            sm_nr:int = cubin['sm'] # type: ignore
            if not sm_nr in sass_c: 
                SM_CuBin_File.cur_sm_nr = sm_nr
                raise SM_Cubin_Unloaded_Cache_Exception("Must load required SM_SASS first!")
            sass:SM_SASS = sass_c[sm_nr]
            if not sm_nr == sass.sm_nr: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        else: 
            # Don't allow anything else
            raise Exception(sp.CONST__ERROR_ILLEGAL)

        self.__cubins_kk = []
        self.__cubins_id = []
        self.__sass = sass
        self.__sm_nr = sm_nr
        self.__selected_kernel = selected_kernel
        self.__no_decode = no_decode

        # The real filename of the binary containing the decoded cuda instructions
        self.__filename:str = cubin['pp'] # type: ignore
        # The absolute or relative path of the binary containing the decoded cuda instructions
        # depending on how SM_CuBin_File was opened
        self.__location:str = file_data[:-len(cubin['pp'])] # type: ignore
        # The bits preceding the bits of the cuda part
        self.__bb_head = cubin['bb'][:cubin['is']] # type: ignore
        # The bits following the bits of the cuda part
        self.__bb_tail = cubin['bb'][cubin['ie']:] # type: ignore

        # This one is supposed to be just a stub
        if no_decode: 
            self.__full_cubin = cubin
            return
        else:
            self.__full_cubin = None

        elf, id, kk = self.initial_decode(cubin, sass_c, wipe, selected_kernel)

        # Generate a control graph using nvdsasm
        # control_flow = SM_Cubin_Graph(cubin['kk'], {u.instr_index:u for u in kk[0].universes}) # type: ignore
        # k:SM_CuBin_Kernel
        # graphs = set()
        # for k in kk:
        #     if not k.kernel_name in control_flow.kernel_graphs:
        #         # Missing a graph? Noooooooo...
        #         raise Exception(sp.CONST__ERROR_UNEXPECTED)
        #     k.add_graph(control_flow.kernel_graphs[k.kernel_name])
        #     graphs.add(k.kernel_name)
        # if not graphs.intersection(set(control_flow.kernel_graphs.keys())) == graphs:
        #     # Do we have a graph that is not needed? Nooooooooooooooo.....
        #     raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # A list with the parsed and decoded instructions inside the cuda part, separatedly for each kernel
        self.__cubins_kk = kk
        # A list with the ids of each decoded kernel (used for the html version)
        self.__cubins_id = id
        # The entire FatBin, containing the Cuda part of the binary
        self.__elf:SM_Cubin_Elf = elf

        # Shortcut to valid replacement values
        self.__valid_regs:SM_CuBin_Regs = SM_CuBin_Regs(self.__sass.sm.details.REGISTERS_DICT)

        # These checks check the integrity as well as showcase how to stitch together the different parts
        # They are not vital for functioning of the module
        # The tests are a cumulative 'startswith' construct
        if not cubin['bb'] == (cubin['bb'][:cubin['is']] + cubin['kk'] + cubin['bb'][cubin['ie']:]):  # type: ignore
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not cubin['bb'].startswith(self.bb_head):  # type: ignore
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        # [DEPRECATED] but still here for reference to demostrate how the parts of a binary stitch together to a whole
        # NOTE: with the partial decoding, this doesn't work!!
        # ============================================================================================================
        # if not cubin['bb'][len(self.bb_head):].startswith(self.cubin_head.bits): 
        #     raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # if not cubin['bb'][(len(self.bb_head) + len(self.cubin_head.bits)):].startswith(b''.join([Instr_CuBin.instr_bwords_to_bytes([j.instr_bits for j in i.universes]) for i in self.cubins_kk])): 
        #     raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # if not cubin['bb'][(len(self.bb_head) + len(self.cubin_head.bits) + len(b''.join([Instr_CuBin.instr_bwords_to_bytes([j.instr_bits for j in i.universes]) for i in self.cubins_kk]))):].startswith(self.cubin_tail.bits): 
        #     raise Exception(sp.CONST__ERROR_UNEXPECTED)
    
    def continue_file_decoding(self, sass_c:SM_SASS|dict, selected_kernel:str):
        """_summary_

        :param sass_c: _description_
        :type sass_c: SM_SASS | dict
        :param selected_kernel: _description_
        :type selected_kernel: str
        :raises Exception: _description_
        :raises Exception: _description_
        :raises Exception: _description_
        """
        # We already loaded the file but now we just want to decode more kernels
        if self.__no_decode: 
            # print("[DEBUG...] Requires start from beginning:", self.__filename)
            self.__no_decode = True
            # If we used no_decode=True, then self.__full_cubin must contain the fully read cubin dictionary.
            # If this is not the case, it's a bug!
            if self.__full_cubin is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            # We have loaded the binary in the past, but only as a stub...
            elf, id, kk = self.initial_decode(self.__full_cubin, sass_c, wipe=False, selected_kernel=selected_kernel)
            # Now that we did the initial decode stage, we can forget __full_cubin
            self.__full_cubin = None

            # A list with the parsed and decoded instructions inside the cuda part, separatedly for each kernel
            self.__cubins_kk = kk
            # A list with the ids of each decoded kernel (used for the html version)
            self.__cubins_id = id
            # The entire FatBin, containing the Cuda part of the binary
            self.__elf:SM_Cubin_Elf = elf

            # Shortcut to valid replacement values
            self.__valid_regs:SM_CuBin_Regs = SM_CuBin_Regs(self.__sass.sm.details.REGISTERS_DICT)
        else:
            # print("[DEBUG...] Can just decode the remaining ones:", self.__filename)
            self.__augment_decode(selected_kernel)

    @property
    def sm_nr(self) -> int: return self.__sm_nr
    @property
    def cubins_kk(self) -> list[SM_CuBin_Kernel]: return self.__cubins_kk
    @property
    def cubins_id(self) -> list[str]: return self.__cubins_id
    @property
    def filename(self) -> str: return self.__filename
    @property
    def location(self) -> str: return self.__location
    @property
    def bb_head(self) -> bytes: return self.__bb_head
    @property
    def bb_tail(self) -> bytes: return self.__bb_tail
    @property
    def elf(self) -> SM_Cubin_Elf: return self.__elf
    # @property
    # def cubin_head(self) -> SM_CuBin_Kernel_Head: return self.__cubin_head
    # @property
    # def cubin_tail(self) -> SM_CuBin_Kernel_Tail: return self.__cubin_tail
    @property
    def valid_regs(self) -> SM_CuBin_Regs: return self.__valid_regs
    @property
    def selected_kernel(self) -> str: return self.__selected_kernel
    @property
    def no_decode(self) -> bool: return self.__no_decode
    
    def __len__(self) -> int:
        return len(self.__cubins_kk)
    def __getitem__(self, index:int):
        return self.__cubins_kk[index]
    def __copy__(self) -> SM_CuBin_File:
        new = self.__new__(self.__class__)
        new.__sass = self.__sass
        new.__sm_nr = self.__sm_nr
        new.__selected_kernel = self.__selected_kernel
        new.__no_decode = self.__no_decode
        new.__cubins_kk = [copy.copy(i) for i in self.__cubins_kk]
        new.__cubins_id = list(self.__cubins_id) # no need to deepcopy this one, just need a new list
        new.__filename = self.__filename
        new.__location = self.__location
        new.__bb_head = self.__bb_head
        new.__bb_tail = self.__bb_tail
        new.__elf = self.__elf # no need to deep copy this one
        new.__valid_regs = self.__valid_regs # no need to deepcopy this one
        new.__full_cubin = self.__full_cubin
        return new
    
    def set_no_decode(self, no_decode:bool):
        self.__no_decode = no_decode

    def initial_decode(self, cubin:dict, sass_c:SM_SASS|dict, wipe:bool, selected_kernel:str):
        # NOTE: !!!! sass_c is actually the SM_SASS cache in the sm_cubin_service.py. If we don't have
        # a required SM_SASS, we must load it into that one and then reference it!!!

        # It may be, that for SMs 70 and 72, the real SM is actually 75. Thus, if decoding doesn't work, 
        try:
            elf, id, kk = SM_CuBin_Kernel.init_kernel_kk(
                self.__sass, self.__sm_nr, 
                hex(cubin['is']), hex(cubin['ie']), cubin['kk'], 
                head_only=False, 
                wipe=wipe, selected_kernel=selected_kernel) # type: ignore
        except CubinDecodeException as error:
            if not self.__init_as_dict: 
                print(tc.colored("[Decoding Error]", color='red', attrs=['bold']) + ": if the SM is 70 or 72, try using 75!")
                raise CubinDecodeException(error.args[0])
            # otherwise... check if we have an SM 70 or 72 and if so, load 75 and check again
            if self.__sm_nr in [70, 72]:
                if not 75 in sass_c:
                    sass_c[75] = SM_SASS(75)
                self.__sass = sass_c[75]
                elf, id, kk = SM_CuBin_Kernel.init_kernel_kk(
                    self.__sass, self.__sm_nr, 
                    hex(cubin['is']), hex(cubin['ie']), cubin['kk'], 
                    head_only=False, wipe=wipe, selected_kernel=selected_kernel) # type: ignore
            else: raise CubinDecodeException(error.args[0])
        return elf, id, kk
    
    def __augment_decode(self, selected_kernel:str):
        # This one is for if we loaded a file already but just one single kernel.
        # Now we want to load another one as well.
        # Thus, if there is something we need, but is not available, it's an unexpected blunder (meaning, a bug)

        # if selected_kernel is '', load all missing kernels
        if selected_kernel == '':
            # print("[DEBUG...] augment decode all")
            cub:SM_CuBin_Kernel
            for cub in self.__cubins_kk:
                cub.deferred_decoding(self.__sass)
        elif selected_kernel == '.':
            # We went from 'All' to 'Single' again and are now trying to decode the 'first' one again
            # print("[DEBUG...] augment decode first")
            self.__cubins_kk[0].deferred_decoding(self.__sass)
        else:
            # We selectively decode another one...
            # First: we must have the kernel name already... => get the index from a mapping
            # print("[DEBUG...] augment decode", selected_kernel)
            mm = self.get_kernel_index_map()
            if not selected_kernel in mm: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            kernel_id = mm[selected_kernel]
            self.__cubins_kk[kernel_id].deferred_decoding(self.__sass)
    
    def reg_count(self) -> dict:
        return self.__elf.reg_count()
    
    def overwrite_reg_count(self, new_reg_count:typing.Dict[str, int]):
        self.__elf.overwrite_reg_count(new_reg_count)
    
    def overwrite_name(self, new_filename:str):
        if not isinstance(new_filename, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__filename = new_filename

    def overwrite_location(self, new_location:str):
        if not isinstance(new_location, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__location = new_location

    def get_kernel_index_map(self) -> typing.Dict[str, int]:
        return {k.kernel_name:ind for ind,k in enumerate(self.__cubins_kk)}

    def get_instr(self, kk_index:int, instr_index:int) -> Instr_CuBin_Repr:
        t:SM_CuBin_Kernel = self.__cubins_kk[kk_index]
        return t.universes[instr_index]

    def create_instr(self, kk_index:int, instr_index:int, class_name:str, enc_vals:dict) -> Instr_CuBin_Repr:
        t:SM_CuBin_Kernel = self.__cubins_kk[kk_index]
        old_instr = t.replace_instruction_by_enc_vals(self.__sass, instr_index, class_name, enc_vals)
        return old_instr
    
    # def create_instr_set_rdwr(self, kk_index:int, instr_index:int, class_name:str, enc_vals:dict, rd:SASS_Bits, wr:SASS_Bits) -> Instr_CuBin_Repr:
    #     t:SM_CuBin_Kernel = self.__cubins_kk[kk_index]
    #     old_instr = t.replace_instruction_by_enc_vals_set_rdwr(self.__sass, instr_index, class_name, enc_vals, rd, wr)
    #     return old_instr

    def replace_instr(self, kk_index:int, instr_index:int, new_instr:Instr_CuBin_Repr) -> Instr_CuBin_Repr:
        t:SM_CuBin_Kernel = self.__cubins_kk[kk_index]
        old_instr = t.replace_instruction_by_universe(self.__sass, instr_index, new_instr)
        return old_instr

    def replace_instr_value(self, kk_index:int, instr_index:int, u_index:int, enc_name:str, new_val_int:int):
        if not isinstance(kk_index, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_index, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(u_index, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(new_val_int, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        kernel:SM_CuBin_Kernel = self.__cubins_kk[kk_index]
        instr:Instr_CuBin_Repr = kernel[instr_index]
        enc_vals = instr.all_enc_vals[u_index]
        # Override an existing value. In this case, we transform the new value
        # into the same format as the existing one requires.
        repl_val:SASS_Bits = enc_vals[enc_name]
        new_val:SASS_Bits = SASS_Bits.from_int(new_val_int, bit_len=repl_val.bit_len, signed=repl_val.signed)
        enc_vals[enc_name] = new_val
        # instr_bits = Instr_CuBin.instr_assemble_to_bv(self.__sass, instr.class_.class_name, enc_vals)
        # kernel.replace_instruction_by_bits(self.__sass, instr_index, instr_bits)
        kernel.replace_instruction_by_enc_vals(self.__sass, instr_index, instr.class_.class_name, enc_vals)

    def set_USCHED_INFO(self, kk_index:int, instr_index:int, u_index:int, usched_info:tuple):
        if not isinstance(usched_info, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not len(usched_info) == 3: raise Exception(sp.CONST__ERROR_ILLEGAL)

        val = usched_info[-1]
        instr:Instr_CuBin_Repr = self.get_instr(kk_index, instr_index)
        if not instr.class_.props.cash_has__usched_info: raise Exception(sp.CONST__CASH_TYPE_NOT_SUPPORTED)
        enc_name:str = str(instr.class_.props.cash_alias__usched_info)
        self.replace_instr_value(kk_index, instr_index, u_index, enc_name, val)

    def set_RD(self, kk_index:int, instr_index:int, u_index:int, rd:int):
        if not isinstance(rd, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not (0 <= rd <= 5): raise Exception(sp.CONST__ERROR_ILLEGAL)

        # RD may be replaced with WR_EARLY in architectures 90 and above...
        instr:Instr_CuBin_Repr = self.get_instr(kk_index, instr_index)
        if not instr.class_.props.cash_has__rd: raise Exception(sp.CONST__CASH_TYPE_NOT_SUPPORTED)
        enc_name:str = str(instr.class_.props.cash_alias__rd)
        self.replace_instr_value(kk_index, instr_index, u_index, enc_name, rd)

    def set_WR_EARLY(self, kk_index:int, instr_index:int, u_index:int, wr:int):
        if not isinstance(wr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not (0 <= wr <= 5): raise Exception(sp.CONST__ERROR_ILLEGAL)

        instr:Instr_CuBin_Repr = self.get_instr(kk_index, instr_index)
        if not instr.class_.props.cash_has__wr_early: raise Exception(sp.CONST__CASH_TYPE_NOT_SUPPORTED)
        enc_name:str = str(instr.class_.props.cash_alias__wr)
        self.replace_instr_value(kk_index, instr_index, u_index, enc_name, wr)

    def set_WR(self, kk_index:int, instr_index:int, u_index:int, wr:int):
        if not isinstance(wr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not (0 <= wr <= 5): raise Exception(sp.CONST__ERROR_ILLEGAL)

        instr:Instr_CuBin_Repr = self.get_instr(kk_index, instr_index)
        if not instr.class_.props.cash_has__wr: raise Exception(sp.CONST__CASH_TYPE_NOT_SUPPORTED)
        enc_name:str = str(instr.class_.props.cash_alias__wr)
        self.replace_instr_value(kk_index, instr_index, u_index, enc_name, wr)
    
    def set_REQ(self, kk_index:int, instr_index:int, u_index:int, req:int):
        if not isinstance(req, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not (0 <= req <= 0b111111): raise Exception(sp.CONST__ERROR_ILLEGAL)

        instr:Instr_CuBin_Repr = self.get_instr(kk_index, instr_index)
        if not instr.class_.props.cash_has__req: raise Exception(sp.CONST__CASH_TYPE_NOT_SUPPORTED)
        enc_name:str = str(instr.class_.props.cash_alias__req)
        self.replace_instr_value(kk_index, instr_index, u_index, enc_name, req)

    def set_BATCH_T(self, kk_index:int, instr_index:int, u_index:int, batch_t:tuple):
        if not isinstance(batch_t, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not len(batch_t) == 3: raise Exception(sp.CONST__ERROR_ILLEGAL)

        val = batch_t[-1]
        instr:Instr_CuBin_Repr = self.get_instr(kk_index, instr_index)
        if not instr.class_.props.cash_has__batch_t: raise Exception(sp.CONST__CASH_TYPE_NOT_SUPPORTED)
        enc_name:str = str(instr.class_.props.cash_alias__batch_t)
        self.replace_instr_value(kk_index, instr_index, u_index, enc_name, val)

    def set_PM_PRED(self, kk_index:int, instr_index:int, u_index:int, pm_pred:tuple):
        if not isinstance(pm_pred, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not len(pm_pred) == 3: raise Exception(sp.CONST__ERROR_ILLEGAL)

        val = pm_pred[-1]
        instr:Instr_CuBin_Repr = self.get_instr(kk_index, instr_index)
        if not instr.class_.props.cash_has__pm_pred: raise Exception(sp.CONST__ERROR_NOT_SUPPORTED)
        enc_name:str = str(instr.class_.props.cash_alias__pm_pred)
        self.replace_instr_value(kk_index, instr_index, u_index, enc_name, val)

    def to_exec(self, file_name:str, test_run=False):
        if(self.__selected_kernel): raise Exception("Can't turn selectively decoded binary into executable file!")
        if(self.__no_decode): raise Exception("Can't turn non decoded binary into an executable file!")

        if self.__elf.arch < 70: raise Exception(sp.CONST__ERROR_NOT_SUPPORTED)

        kk_head:bytes
        kk_original_instr_bytes:bytes
        kk_tail:bytes
        
        # Get head and tail ends of the exe, as well as the required size of the middle part that holds the instructions
        kk_head, kk_original_instr_bytes, kk_tail = self.__elf.head_and_tail_to_exec()
        
        # Assemble the (potentially changed) instructions into bytes
        # Need to sort all the kernels in ascending order by their respective offset.
        # NOTE: failing to sort them properly will result in a rather chaotic binary file where nothing is as it seems ^^
        kk_instr = [Instr_CuBin.instr_bwords_to_bytes([j.instr_bits for j in i.universes]) for i in sorted(self.cubins_kk, key=lambda k:k.kernel_offset_hex)]
        instr_bytes = b''.join(kk_instr)
        
        # Concatenate everything
        bb = self.bb_head + kk_head + instr_bytes + kk_tail + self.bb_tail

        if test_run:
            # The assembled, potentially changed instruction bytes must be of the same length as the original
            # instructions, contained in the fatbin ELF
            if not (len(instr_bytes) == len(kk_original_instr_bytes)):
                raise Exception(sp.CONST__ERROR_ILLEGAL)
            bb_test = self.bb_head + kk_head + kk_original_instr_bytes + kk_tail + self.bb_tail
            if not (bb == bb_test):
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
        else:
            with open(file_name, 'wb') as f:
                f.write(bb)
