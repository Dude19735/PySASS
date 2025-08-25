"""
https://gist.github.com/x0nu11byt3/bcb35c3de461e5fb66173071a2379779
"""
import typing
import io
from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from elftools.elf.sections import NullSection
from elftools.elf.sections import StringTableSection
from elftools.elf.sections import SymbolTableSection
from elftools.elf.sections import Section
from elftools.construct.lib.container import Container
from . import _config as sp
from .sm_cubin_lib import SM_CuBin_Lib

class ElfData:
    def __init__(self, section:Section, index:int):
        self.__index = index
        self.__data = bytearray(section.data())
        self.__sh_offset = section['sh_offset']
        self.__data_size = section.data_size
        self.__name = section.name

    @property
    def index(self) -> int: return self.__index
    @property
    def data(self) -> bytearray: return self.__data
    @property
    def data_size(self) -> int: return self.__data_size
    @property
    def sh_offset(self) -> int: return self.__sh_offset
    @property
    def name(self) -> str: return self.__name

class SM_Elf:
    def __init__(self, name:str, arch_range:set, index:int):
        if not isinstance(name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(arch_range, set): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not min(arch_range) >= 50: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not max(arch_range) <= 120: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(index, int): raise Exception(sp.CONST__ERROR_ILLEGAL)

        self.__name:str = name
        self.__arch_range:set = arch_range
        self.__nv_info:ElfData = None # type: ignore
        self.__text:ElfData = None # type: ignore
        self.__nv_constants:typing.Dict[str, ElfData] = dict()
        self.__misc:typing.List[ElfData] = []
        self.__index = index

    @property
    def offset_hex(self) -> str: return hex(self.__text.sh_offset)
    @property
    def name(self) -> str: return self.__name
    @property
    def arch_range(self) -> set: return self.__arch_range
    @property
    def nv_info(self) -> ElfData: return self.__nv_info
    @property
    def text(self) -> ElfData: return self.__text
    @property
    def nv_constants(self) -> typing.Dict[str, ElfData]: return self.__nv_constants
    @property
    def index(self) -> int: return self.__index

    def add(self, elf_data:ElfData):
        # Add ELF data bits.
        # NOTE: this method can be used to catch unexpected names: uncomment the exception
        #       in the 'else' portion of the statement.
        if not isinstance(elf_data, ElfData): raise Exception(sp.CONST__ERROR_ILLEGAL)
        name:str = elf_data.name
        if name.startswith('.nv.info'):
            self.__add_nv_info(elf_data)
        elif name.startswith('.nv.constant'):
            self.__add_constant(elf_data)
        elif name.startswith('.text'):
            self.__add_text(elf_data)
        elif name.startswith('.nv.capmerc'):
            self.__misc.append(elf_data)
        elif name.startswith('.nv.merc.nv.info'):
            self.__misc.append(elf_data)
        elif name.startswith('.rela.text'):
            self.__misc.append(elf_data)
        else:
            self.__misc.append(elf_data)
            # raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

    def words(self):
        return SM_CuBin_Lib.bits_to_words(self.__text.data)

    def __add_constant(self, const:ElfData):
        if not isinstance(const, ElfData): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__nv_constants[const.name] = const
    def __add_text(self, text:ElfData):
        if not isinstance(text, ElfData): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if self.__text is not None: raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__text = text
    def __add_nv_info(self, info:ElfData):
        if not isinstance(info, ElfData): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if self.__nv_info is not None: raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__nv_info = info

class SM_Elf_86(SM_Elf):
    def __init__(self, name:str, arch:int, index:int):
        if not isinstance(name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(arch, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        super().__init__(name, {50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86}, index)
        if not arch in self.arch_range: raise Exception(sp.CONST__ERROR_ILLEGAL)

class SM_Elf_90(SM_Elf):
    def __init__(self, name:str, arch:int, index:int):
        if not isinstance(name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(arch, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        super().__init__(name, {90}, index)
        if not arch in self.arch_range: raise Exception(sp.CONST__ERROR_ILLEGAL)

class SM_Elf_120(SM_Elf):
    def __init__(self, name:str, arch:int, index:int):
        if not isinstance(name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(arch, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        super().__init__(name, {100, 120}, index)
        if not arch in self.arch_range: raise Exception(sp.CONST__ERROR_ILLEGAL)

class SM_Cubin_Elf:
    """
    This class maps a Cubin Elf to something more insightful.

    ### The following outlines the used elf sections
    #### .shstrtab (StringTableSection)
    * contains a list of all used symbols

    #### .strtab (StringTableSection)
    This part contains some more intersting bits of text. For example
    * text._Z7kernelCjPm\x00.nv.info._Z7kernelCjPm\x00.nv.shared._Z7kernelCjPm\x00.rel.nv.constant0._Z7kernelCjPm\x00.nv.constant0._Z7kernelCjPm\x00
    
    Each section starts with ".text" followed directly by the name of the kernel. In this case, this is "_Z7kernelCjPm".

    Commonly, it contains the following sub-sections:
    * .nv.info
        * probably contains the header data
    * .text
        * shibboleted name of the kernel
    * .nv.info.[kernel_name]
    * .nv.shared.[kernel_name]
        * seems to point to shared memory sections
        * this one is more extensive in SM 90 and above
    * .rel.nv.constant[x].[kernel_name]
    * .nv.constant[X].[kernel_name]
        * contains constant values
        * there may be multiple of these
        * .nv.constant0.[kernel_name] is always present and contains the zeros between the last info bits to the first instruction bits.
    * .debug_frame
        * a bunch of bits
    * .rel.debug_frame
        * another bunch of bits
    * .rela.debug_frame
        * this one doesn't seem to exist 
    * .nv.callgraph
    * .nv.prototype
        * contains the names of the kernels
    * .nv.rel.action

    #### Sections
    The ELF starts with 
    * .shstrtab
    * .strtab
    * .symtab
    Then follows the first debug_frame
    * .debug_frame
    Then follow all nv.info, nv.callgraph and .nv.rel.acion (maybe more)
    * .nv.info
    * .nv.info._Z7kernelCjPm
    * .nv.info._Z7kernelBjPm
    * .nv.info._Z7kernelAjPm
    * .nv.callgraph
    * .nv.rel.action
    Then follows the next debug frame .rel.debug_frame
    * .rel.debug_frame
    At the end is the code and related constant stuff
    * .nv.constant0._Z7kernelCjPm
    * .nv.constant0._Z7kernelBjPm
    * .nv.constant0._Z7kernelAjPm
    * .text._Z7kernelCjPm
    * .text._Z7kernelBjPm
    * .text._Z7kernelAjPm
    """
    def __init__(self, arch:int, bits:bytes):
        elf = ELFFile(io.BytesIO(bits))
        self.__arch = arch
        # The header is not included in the sections of the ELF => keep it
        self.__header:Container = elf.header
        self.__header_bytes = bits[:elf.header['e_ehsize']]

        self.__null:ElfData = None # type: ignore
        self.__shstrtab:ElfData = None # type: ignore
        self.__strtab:ElfData = None # type: ignore
        self.__symtab:ElfData = None # type: ignore
        self.__nv_info:ElfData = None # type: ignore
        self.__nv_callgraph:ElfData = None # type: ignore
        self.__nv_rel_action:ElfData = None # type: ignore # SM 86--
        self.__debug_frames:list = []
        self.__misc:list = []

        self.__sequence:list = []

        if arch <= 86:
            self.__kernel = self.__process_strtab_86(arch, elf)
        elif arch <= 90:
            self.__kernel = self.__process_strtab_90(arch, elf)
        elif arch <= 120:
            self.__kernel = self.__process_strtab_120(arch, elf)
        else:
            raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        # [print(sect.name) for sect in elf.iter_sections()]
        # with open("elf_{0}.txt".format(arch), 'w') as f:
        #     for sect in elf.iter_sections():
        #         f.write(sect.name)
        #         f.write('\n') 
        #         f.write(str(sect.data()))
        #         f.write('\n\n')

        self.__process_elf(self.__arch, elf, self.__kernel)
        offsets = sorted([(i.sh_offset, i.sh_offset + i.data_size) for i in self.__sequence], key=lambda x: x[0], reverse=True)

        # There is also a tail that isn't decoded properly by a standard ELF decode run.
        # Keep it as well.
        self.__tail_bytes = bits[offsets[0][1]:]
    
    @property
    def arch(self) -> int: return self.__arch
    @property
    def header(self) -> Container: return self.__header
    @property
    def null(self) -> ElfData: return self.__null
    @property
    def shstrtab(self) -> ElfData: return self.__shstrtab
    @property
    def strtab(self) -> ElfData: return self.__strtab
    @property
    def symtab(self) -> ElfData: return self.__symtab
    @property
    def nv_info(self) -> ElfData: return self.__nv_info
    @property
    def nv_callgraph(self) -> ElfData: return self.__nv_callgraph
    @property
    def nv_rel_action(self) -> ElfData: return self.__nv_rel_action
    @property
    def debug_frames(self) -> typing.List[ElfData]: return self.__debug_frames
    @property
    def misc(self) -> typing.List[ElfData]: return self.__misc
    @property
    def kernel(self) -> typing.Dict[str,SM_Elf_86]|typing.Dict[str,SM_Elf_90]|typing.Dict[str,SM_Elf_120]: return self.__kernel
    
    def reg_count(self) -> dict:
        reg_counts = dict()
        k:SM_Elf
        for n,k in self.kernel.items():
            reg_counts[n] = self.__nv_info.data[24*k.index + 8]
        return reg_counts
    
    def overwrite_reg_count(self, new_reg_count:typing.Dict[str, int]):
        if not isinstance(new_reg_count, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(k,str) and k in self.__kernel for k in new_reg_count.keys()): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(k,int) for k in new_reg_count.values()): raise Exception(sp.CONST__ERROR_ILLEGAL)

        for n,r in new_reg_count.items():
            self.__nv_info.data[24*self.kernel[n].index + 8] = r

    def __get_offsets(self) -> list:
        offsets = [(i1.sh_offset, i2.sh_offset - i1.sh_offset, i1) for i1,i2 in zip(self.__sequence[1:-1], self.__sequence[2:])]
        offsets.append((self.__sequence[-1].sh_offset, self.__sequence[-1].data_size, self.__sequence[-1]))
        return offsets

    def to_exec(self) -> bytes:
        offsets = self.__get_offsets()

        # The first bit of the cubin is the regular ELF header.
        # This one should be 64 bytes long.
        res = [self.__header_bytes]
        # Jumpstart the cur_size to 64
        cur_size = len(self.__header_bytes)
        
        # check... offset+size == next(offset)
        if not all(x[0]+x[1] == y[0] for x,y in zip(offsets[:-1], offsets[1:])):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # the first bunch of bytes are not what they are supposed to be, if this check fails
        if not len(self.__header_bytes) == offsets[0][0]:
            raise Exception(sp.CONST__ERROR_UNEXPECTED)

        section:ElfData
        size:int
        for ind,(offset, size, section) in enumerate(offsets):
            if not (offset == cur_size):
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            
            # Add the next bit of data
            res.append(bytes(section.data))
            # If we have some alignment or other kind of offset
            # add the missing gap as zeros
            if size > section.data_size:
                res.append(b'\x00'*(size - section.data_size))
            cur_size += size

        res.append(self.__tail_bytes)
        return b''.join(res)
    
    def head_and_tail_to_exec(self) -> typing.Tuple[bytes, bytes, bytes]:
        offsets = self.__get_offsets()

        # The first bit of the cubin is the regular ELF header.
        # This one should be 64 bytes long.
        head_res = [self.__header_bytes]
        # Jumpstart the cur_size to 64
        cur_size = len(self.__header_bytes)
        
        # check... offset+size == next(offset)
        if not all(x[0]+x[1] == y[0] for x,y in zip(offsets[:-1], offsets[1:])):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # the first bunch of bytes are not what they are supposed to be, if this check fails
        if not len(self.__header_bytes) == offsets[0][0]:
            raise Exception(sp.CONST__ERROR_UNEXPECTED)

        section:ElfData
        size:int
        ind = 0
        # Collect all the parts in front of the instructions
        for ind,(offset, size, section) in enumerate(offsets):
            # stop as soon as we hit a text section
            if section.name.startswith('.text'): break

            if not (offset == cur_size):
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            
            # Add the next bit of data
            head_res.append(bytes(section.data))
            # If we have some alignment or other kind of offset
            # add the missing gap as zeros
            if size > section.data_size:
                head_res.append(b'\x00'*(size - section.data_size))
            cur_size += size

        # Skip the part with the instructions
        # NOTE: 'ind' points to the first '.text' entry => no +-1 for the iterator
        instr_res = []
        instr_size = 0
        size_offset = cur_size
        ind2 = ind
        for offset, size, section in offsets[ind:]:
            if not section.name.startswith('.text'): break

            if not (offset == instr_size + size_offset):
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            
            # Add the next bit of data
            instr_res.append(bytes(section.data))
            # If we have some alignment or other kind of offset
            # add the missing gap as zeros
            if size > section.data_size:
                instr_res.append(b'\x00'*(size - section.data_size))
            instr_size += size
            ind2 += 1

        instr_bytes = b''.join(instr_res)
        if not len(instr_bytes) == instr_size:
            raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # NOTE: 'ind2' points to the last '.text' entry (because of the 'not' in the break condition) => do +1 for tail_ind
        tail_ind = ind2

        # The index where the tail end of the exe starts:
        #  - :ind == everything up to the start of the instructions
        #  - :ind2 == everything up to the end of the instructions => subtract 1 from it for the tail_ind
        size_offset += instr_size
        tail_res = []
        cur_size = 0
        # Collect the remaining part after the instructions.
        for offset, size, section in offsets[tail_ind:]:
            if not (offset == cur_size+size_offset):
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            # Add the next bit of data
            tail_res.append(bytes(section.data))
            # If we have some alignment or other kind of offset
            # add the missing gap as zeros
            if size > section.data_size:
                tail_res.append(b'\x00'*(size - section.data_size))
            cur_size += size
        tail_res.append(self.__tail_bytes)

        return b''.join(head_res), instr_bytes, b''.join(tail_res)

    def __process_strtab_86(self, arch:int, elf:ELFFile) -> typing.Dict[str, SM_Elf_86]:
        strtab_l = [sect.data() for sect in elf.iter_sections() if sect.name == '.strtab']
        if not len(strtab_l) == 1:
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        strtab:bytes = strtab_l[0]
        if not strtab.startswith(b'\x00.shstrtab\x00.strtab\x00.symtab\x00.symtab_shndx\x00'):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        strlist = [x for x in strtab.decode('utf-8').split('\x00') if x]
        kernel = []
        index = 0
        for x in strlist:
            if x.startswith('.text'):
                kernel.append((x[6:],SM_Elf_86(x[6:], arch, index)))
                index += 1
        return dict(kernel)

    def __process_strtab_90(self, arch:int, elf:ELFFile) -> typing.Dict[str, SM_Elf_90]:
        strtab_l = [sect.data() for sect in elf.iter_sections() if sect.name == '.strtab']
        if not len(strtab_l) == 1:
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        strtab:bytes = strtab_l[0]
        if not strtab.startswith(b'\x00.shstrtab\x00.strtab\x00.symtab\x00.symtab_shndx\x00'):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        strlist = [x for x in strtab.decode('utf-8').split('\x00') if x]
        kernel = []
        index = 0
        for x in strlist:
            if x.startswith('.text'):
                kernel.append((x[6:],SM_Elf_90(x[6:], arch, index)))
                index += 1
        return dict(kernel)

    def __process_strtab_120(self, arch:int, elf:ELFFile) -> typing.Dict[str, SM_Elf_120]:
        strtab_l = [sect.data() for sect in elf.iter_sections() if sect.name == '.strtab']
        if not len(strtab_l) == 1:
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        strtab:bytes = strtab_l[0]
        if not strtab.startswith(b'\x00.shstrtab\x00.strtab\x00.symtab\x00.symtab_shndx\x00'):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        strlist = [x for x in strtab.decode('utf-8').split('\x00') if x]
        kernel = []
        index = 0
        for x in strlist:
            if x.startswith('.text'):
                kernel.append((x[6:],SM_Elf_120(x[6:], arch, index)))
                index += 1
        return dict(kernel)
    
    def __process_elf(self, arch:int, elf:ELFFile, kernel:typing.Dict[str, SM_Elf_86]|typing.Dict[str, SM_Elf_90]|typing.Dict[str, SM_Elf_120]):
        if arch == 86:
            pass
        for elf_sect in elf.iter_sections():
            sect:ElfData = ElfData(elf_sect, len(self.__sequence))
            self.__sequence.append(sect)
            if not sect.name: 
                self.__null = sect
                continue
            nn = sect.name.split('.')
            if nn[-1] in kernel:
                kernel[nn[-1]].add(sect)
            elif nn[-1] == 'shstrtab': 
                self.__shstrtab = sect
            elif nn[-1] == 'strtab': 
                self.__strtab = sect
            elif nn[-1] == 'symtab': 
                self.__symtab = sect
            elif nn[-1] == 'info': 
                self.__nv_info = sect
            elif nn[-1] == 'callgraph': 
                self.__nv_callgraph = sect
            elif nn[-1] == 'action': 
                self.__nv_rel_action = sect
            elif nn[-1] == 'debug_frame':
                self.__debug_frames.append(sect)
            elif len(nn) == 5 and nn[-2] == 'reserved':
                self.__misc.append(sect)
                # remove this entry cause no data actually present...
                self.__sequence = self.__sequence[:-1]
            elif nn[-1] == 'tkinfo':
                self.__misc.append(sect)
            elif nn[-1] == 'cuver':
                self.__misc.append(sect)
            elif nn[-1] == 'compat':
                self.__misc.append(sect)
            elif nn[-1] == 'constant4':
                self.__misc.append(sect)
            elif len(nn) == 4 and nn[-2] == 'global' and nn[-1] == 'init':
                self.__misc.append(sect)
            elif len(nn) == 7 and nn[-2] == 'reserved' and nn[2] == 'merc':
                self.__misc.append(sect)
                # remove this entry cause no data actually present...
                self.__sequence = self.__sequence[:-1]
            else:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        
        self.__sequence = sorted(self.__sequence, key=lambda x: x.sh_offset)

