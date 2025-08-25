import os
import re
from . import _config as sp
from py_sass import SM_SASS
from py_sass_ext import BitVector
from py_sass_ext import SASS_Bits
from py_sass_ext import SASS_Range

"""
This file contains methods that are used to interact with a real cubin's actual bits.
For example how to read it, how to find the kernels and how to decode it.
"""

class SM_CuBin_Lib:
    @staticmethod
    def bits_to_words(bits:bytes, w_len=8):
        xx = [hex(i)[2:].zfill(2) for i in bits]
        words = [xx[i:(i+w_len)] for i in range(0,len(xx),8)]
        return words

    @staticmethod
    def word_to_val(word:list) -> int:
        if len(word) == 0: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(word[0], str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        w_len = len(word)
        val_10 = sum([int(i,16)<<(w_len*ind) for ind,i in enumerate(word)])
        return val_10
    
    @staticmethod
    def read_arch(is_blackwell:bool, bits:bytes) -> int:
        if is_blackwell: arch = int(bits[6*8+1])
        else: arch = int(bits[6*8])
        return arch
    
    @staticmethod
    def read_arch_b(bits:bytes) -> int:
        is_blackwell = int(bits[8]) == 8
        return SM_CuBin_Lib.read_arch(is_blackwell, bits)
    
    @staticmethod
    def read_end_of_sass(arch:int, words:list) -> int:
        if arch <= 86: end_of_sass = SM_CuBin_Lib.word_to_val(words[5])
        elif 90<=arch and arch<=120: end_of_sass = SM_CuBin_Lib.word_to_val(words[-6])
        else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        return end_of_sass
    
    @staticmethod
    def read_begin_of_sass(arch:int, words:list) -> tuple:
        if arch <= 86: 
            end_of_conf = SM_CuBin_Lib.word_to_val(words[int((SM_CuBin_Lib.word_to_val(words[4])) / 8)+8])
            ind = int(end_of_conf/8)
            offset = 0
            zz = 8*['00']
            for w in words[ind:]:
                if w != zz: break
                offset += 1
            begin_of_sass = int((ind+offset)*8)
        elif 90<=arch and arch<=120: 
            begin_of_sass = SM_CuBin_Lib.word_to_val(words[-20])
            ind = int(begin_of_sass/8)
            offset = 0
            zz = 8*['00']
            for w in reversed(words[:ind]):
                if w != zz: break
                offset += 1
            end_of_conf = int((ind-offset)*8)
        else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        return end_of_conf, begin_of_sass
    
    @staticmethod
    def count_kernel(arch:int, end_of_config:int, words:list) -> int:
        # This one doesn't work properly yet...
        # For now, assume we have one kernel
        # Work ongoing...
        if arch <= 62: return 1

        index = int(end_of_config/8)-1
        counter = 0
        while words[index][0] == '02':
            counter+=1
            if arch <= 86: index -= 2
            elif 90<=arch and arch<=120: index -= 3
            else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        return counter
    
    @staticmethod
    def read_kernel_names(arch:int, bits:bytes) -> list:
        # marker for kernel name location
        target = b'nv.callgraph'

        # find the last index of target, which is a good location for the kernel names
        kernels_name_start = [(m.group(), m.start(), m.end()) for m in re.finditer(target, bits)]
        b_ind = kernels_name_start[-1][-1]
        b_ind_2 = bits[b_ind:].find(b'\x00.')
        ind = b_ind + b_ind_2 + 2

        # cut them out
        if arch <= 86: b_end = bits[ind:].find(b'\x00\x00')
        elif 90<=arch and arch<=120: b_end = bits[ind:].find(b'\x00.')
        else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        
        # clean them up
        ll = bits[ind:(ind+b_end)].split(b'\x00')
        kernel_names = [i.decode('utf-8') for i in ll if i.startswith(b'_')]
        return kernel_names
    
    @staticmethod
    def read_kernel_offsets(arch:int, kernel_names:list, words:list):
        # kernel = []
        offsets = []
        # Decode scheme
        if arch <= 86:
            # SM 50 to 86
            # ===========
            # 1. read all words as 8 byte packs
            # 2. assume N kernels in the cubin
            # 3. kernel offset for kernel position i: len(words) - (26) + (i-N)*(8)
            #     => Nth kernel at -26*8 - 0*(8*8)
            #     => (N-1)th kernel at -26*8 - 1*(8*8)
            #     => (N-2)th kernel at -26*8 - 2*(8*8)
            #        ...
            N = len(kernel_names)
            for i,k in enumerate(kernel_names):
                offsets.append(len(words) - 26 + (i+1-N)*8)

        elif arch <= 90:
            # SM 90
            # ===========
            # 1. read all words as 8 byte packs
            # 2. assume N kernels in the cubin
            # 3. kernel offset for kernel position i: len(words) - ((56+8*(N-1)) + (i-N)*(8)
            N = len(kernel_names)
            for i,k in enumerate(kernel_names):
                offsets.append(len(words) - (56 + 8*(N-1)) + (i+1-N)*(8))

        elif arch <= 120:
            # SM 100 and 120
            # ==============
            # 1. read all words as 8 byte packs
            # 2. assume N kernels in the cubin
            # 3. kernel offset for kernel position i: len(words) - ((112+24*(N-1)) + (i-N)*(8)
            N = len(kernel_names)
            for i,k in enumerate(kernel_names):
                offsets.append(len(words) - (112 + 24*(N-1)) + (i+1-N)*(8))

        else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        
        offset_kernels = [SM_CuBin_Lib.word_to_val(words[i]) for i in offsets]
        kernel_offsets_hex = [hex(x) for x in offset_kernels]

        word_index_kernels = [int(i/8) for i in offset_kernels]
        last_ind = word_index_kernels[-1]
        for w in words[word_index_kernels[-1]:]:
            if w == 8*['00']: break
            last_ind += 1
        word_index_kernels.append(last_ind)

        kernel_words = []
        for i in range(1,len(word_index_kernels)):
            kernel_words.append(words[word_index_kernels[i-1]:word_index_kernels[i]])

        head_words = words[:word_index_kernels[0]]
        tail_words = words[word_index_kernels[-1]:]
        return head_words, kernel_words, kernel_offsets_hex, tail_words

    @staticmethod
    def read_cubin(path:str) -> dict[str, list]:
        bins = [i for i in os.listdir(path) if not (i.endswith(".cubin") or i.endswith(".log"))]

        sys_dump = "cd {0} && cuobjdump {1} -xelf all && cd .."
        for bin in bins:
            os.system(sys_dump.format(path, bin))

        # cuobjdump creates temporary files => remove them
        temps = [path + "/" + i for i in os.listdir(path) if (i.startswith("tmpxft") and i.endswith(".cubin"))]
        for temp in temps: 
            if os.path.exists(temp) and os.path.isfile(temp):
                os.remove(temp)

        cubins = [path + "/" + i for i in os.listdir(path) if i.endswith(".cubin")]
        return cubins
    
    @staticmethod
    def read_ncod_full(path:str) -> dict[str, object]:
        with open(path, 'rb') as f:
            bits = f.read()
            return SM_CuBin_Lib.read_ncod_full_b(bits, path)

    @staticmethod
    def read_ncod_full_b(bits:bytes, path:str='') -> dict[str, object]:
        # find all binary starts
        ksi = [(m.start(), m.end()) for m in re.finditer(b'\x7f\x45\x4c\x46\x02\x01\x01', bits)]
        # find the one that is cuda
        #  0x33 for x <= 90, 0x41 for 90 < x <= 120
        if not (len([k[0] for k in ksi if hex(bits[k[1]]) in ['0x33', '0x41']])==1): raise Exception("No Cuda kernel found")
        kernel_start_ind = [k[0] for k in ksi if hex(bits[k[1]]) in ['0x33', '0x41']][0]
        
        # find the offset to close the end of the kernel
        offset_w = SM_CuBin_Lib.bits_to_words(bits[(kernel_start_ind+32):][:8])
        # convert the offset to an integer and add it to the kernel start index
        kernel_semi_end_ind = SM_CuBin_Lib.word_to_val(offset_w[0]) + kernel_start_ind
        # find the place where the kernel definitely ends
        kernel_end_ind = kernel_semi_end_ind + bits[kernel_semi_end_ind:].find(b'\x01\x1b\x03\x3b')

        if path: pp = path.split('/')[-1]
        else: pp = 'N/A'
        k_bits = bits[kernel_start_ind:kernel_end_ind]
        # return the entire kernel
        return {
            'pp':pp, # path location of binary
            'kk':k_bits, # bytes of the Cuda part
            'sm':SM_CuBin_Lib.read_arch_b(k_bits), # integer refering to architecture
            'bb':bits, # entire binary file
            'is':kernel_start_ind, # start index into bb for cuda part
            'ie':kernel_end_ind # end index into bb for cuda part
        }
    
    @staticmethod
    def hex_words_to_bin(sass:SM_SASS, kernel_words:list) -> list:
        enc_width = sass.sm.details.FUNIT.encoding_width
        word_size = sass.sm.details.ARCHITECTURE.WORD_SIZE
        kernel_bits = []
        for ww in kernel_words:
            bb = [[bin(int(i,16))[2:].zfill(8) for i in s] for s in ww]
            bits = [BitVector([int(i) for i in "".join(reversed(b)).zfill(enc_width)][-word_size:]) for b in bb]
            kernel_bits.append(bits)
        return kernel_bits
    
    @staticmethod
    def args_to_bytes(args:dict):
        def sass_2_b(v):
            if isinstance(v, set):
                return str(len(v)).zfill(2).encode('utf-8') + b''.join([vv.encode() for vv in v])
            elif isinstance(v, SASS_Range):
                return "00".encode('utf-8') + v.encode()
            else: raise Exception(sp.CONST__ERROR_ILLEGAL)
        return b''.join(k.encode('utf-8') + b':' + sass_2_b(v) for k,v in args.items())
    
    @staticmethod
    def bytes_to_args(bb:bytes):
        res = dict()
        ii = 0
        while len(bb) > 0:
            ii = bb.find(b':')
            arg_name = bb[:ii].decode('utf-8')
            ii += 1
            slen = int(bb[ii:(ii+2)].decode('utf-8'))
            ii+=2
            if slen == 0:
                l = bb[ii]
                if not l == 27: raise Exception(sp.CONST__ERROR_ILLEGAL)
                res[arg_name] = SASS_Range.decode(bb[ii:(ii+l)])
                ii += l
            else:
                arg_val = set()
                for i in range(0, slen):
                    l = bb[ii]
                    if l == 11: arg_val.add(SASS_Bits.decode(bb[ii:(ii+l)]))
                    elif l == 27: raise Exception(sp.CONST__ERROR_ILLEGAL)
                    else: raise Exception(sp.CONST__ERROR_ILLEGAL)
                    ii += l
                res[arg_name] = arg_val
            bb = bb[ii:]
        return res
    
    @staticmethod
    def get_url(ip:str, port:int):
        return "http://{ip}:{port}".format(ip=ip, port=port)

if __name__ == '__main__':
    x = {
        'Pg@not': {SASS_Bits.from_int(0), SASS_Bits.from_int(1)}, 
        'Pg': {SASS_Bits.from_int(1)},
        'Puget@Sound': SASS_Range(0,10,10,1,0),
        'usched_info': {SASS_Bits.from_int(2)}, 
        'pm_pred': {SASS_Bits.from_int(3)}, 
        'req_bit_set': {SASS_Bits.from_int(4), SASS_Bits.from_int(5), SASS_Bits.from_int(6)}
    }
    bb = SM_CuBin_Lib.args_to_bytes(x)
    bb_dec = SM_CuBin_Lib.bytes_to_args(bb)
    pass
    