import sqlite3
import typing
import gzip
from py_sass import SM_SASS
from . import _config as sp
from ._instr_cubin_db_proxy import Db_Binary_Proxy, Db_BinaryData_Proxy, Db_BinaryMisc_Proxy, Db_Kernel_Proxy, Db_BinaryMisc_Proxy
from .sm_cubin_kernel import SM_CuBin_Kernel
from .sm_cubin_file import SM_CuBin_File
from .sm_cubin_kernel_ht import SM_CuBin_Kernel_Head, SM_CuBin_Kernel_Tail

class SM_Cubin_DB:
    DB_VERSION = '1.2'
    DB_VERSION_DESC = 'Contains AdditionalInfo everywhere with added information in some places. Support for multiple bins in one db file.'
    @staticmethod
    def persist_bins(bins:typing.List[Db_Binary_Proxy]) -> sqlite3.Connection:
        if not isinstance(bins, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_Binary_Proxy) for c in bins): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return Db_Binary_Proxy.persist(bins)

    @staticmethod
    def db_con_to_mem(db_con:sqlite3.Connection, compress=True) -> bytes:
        if not isinstance(db_con, sqlite3.Connection): raise Exception(sp.CONST__ERROR_ILLEGAL)
        bb = db_con.serialize()
        if compress: return gzip.compress(bb)
        else: return bb
    
    @staticmethod
    def db_mem_to_con(db_mem:bytes, compressed=True):
        if not isinstance(db_mem, bytes): raise Exception(sp.CONST__ERROR_ILLEGAL)
        db_con = sqlite3.Connection(':memory:')
        if compressed:
            bb = gzip.decompress(db_mem)
            db_con.deserialize(bb)
        else: db_con.deserialize(db_mem)
        return db_con

    @staticmethod
    def db_con_to_file(db_con:sqlite3.Connection, filename:str):
        if not isinstance(db_con, sqlite3.Connection): raise Exception(sp.CONST__ERROR_ILLEGAL)
        bb = db_con.serialize()
        with open(filename, 'wb') as f:
            f.write(bb)
        # f_con = sqlite3.Connection(filename)
        # db_con.backup(f_con)
        # f_con.close()

    @staticmethod
    def kernel_list_to_db(sass:SM_SASS, all_kernels:typing.List[SM_CuBin_Kernel]) -> typing.List[Db_Kernel_Proxy]:
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(all_kernels, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(kk, SM_CuBin_Kernel) for kk in all_kernels): raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        kk:SM_CuBin_Kernel
        db_kernel = []
        for kk in all_kernels:
            db_kernel.append(kk.to_db(sass))
        
        return db_kernel
    
    @staticmethod
    def kernel_list_to_db_test(sass:SM_SASS, all_kernels:typing.List[SM_CuBin_Kernel]) -> Db_Binary_Proxy:
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(all_kernels, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(kk, SM_CuBin_Kernel) for kk in all_kernels): raise Exception(sp.CONST__ERROR_ILLEGAL)

        binary_name:str = "lol_test"
        db_kernel:typing.List[Db_Kernel_Proxy] = SM_Cubin_DB.kernel_list_to_db(sass, all_kernels)
        
        misc = [
            Db_BinaryMisc_Proxy.create(Db_BinaryMisc_Proxy.Type_Version, 0, SM_Cubin_DB.DB_VERSION, SM_Cubin_DB.DB_VERSION_DESC),
            Db_BinaryMisc_Proxy.create(Db_BinaryMisc_Proxy.Type_EncW, 1, str(sass.sm.details.FUNIT.encoding_width), 'Size of a complete instruction in bits'), # type: ignore
            Db_BinaryMisc_Proxy.create(Db_BinaryMisc_Proxy.Type_WordSize, 2, str(sass.sm.details.ARCHITECTURE.WORD_SIZE), 'Size of a complete word in bits'), # type: ignore
            Db_BinaryMisc_Proxy.create(Db_BinaryMisc_Proxy.Type_TestRun, 3, 'This is a test run', 'Some random comment')
        ]
        return Db_Binary_Proxy.create(sass, 0, binary_name, db_kernel, [],  misc, 'The entry point to a decoded binary')

    @staticmethod
    def file_to_db_partial(sass:SM_SASS, cubin:SM_CuBin_File) -> Db_Binary_Proxy:
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cubin, SM_CuBin_File): raise Exception(sp.CONST__ERROR_ILLEGAL)

        binary_name:str = cubin.filename
        all_id:typing.List[str] =  cubin.cubins_id
        all_kernels:typing.List[SM_CuBin_Kernel] = cubin.cubins_kk

        # cubin_head:SM_CuBin_Kernel_Head = cubin.cubin_head
        # cubin_tail:SM_CuBin_Kernel_Tail = cubin.cubin_tail

        # db_cbh:Db_BinaryData_Proxy = cubin_head.to_db()
        # db_cbt:Db_BinaryData_Proxy = cubin_tail.to_db()
        db_kernel:typing.List[Db_Kernel_Proxy] = SM_Cubin_DB.kernel_list_to_db(sass, all_kernels)
        
        misc = [
            Db_BinaryMisc_Proxy.create(Db_BinaryMisc_Proxy.Type_Version, 0, SM_Cubin_DB.DB_VERSION, SM_Cubin_DB.DB_VERSION_DESC),
            Db_BinaryMisc_Proxy.create(Db_BinaryMisc_Proxy.Type_EncW, 1, str(sass.sm.details.FUNIT.encoding_width), 'Size of a complete instruction in bits'), # type: ignore
            Db_BinaryMisc_Proxy.create(Db_BinaryMisc_Proxy.Type_WordSize, 2, str(sass.sm.details.ARCHITECTURE.WORD_SIZE), 'Size of a complete word in bits'), # type: ignore
            Db_BinaryMisc_Proxy.create(Db_BinaryMisc_Proxy.Type_FullName, 3, cubin.location + "/" + cubin.filename, 'Full path as passed to the decoder'),
            Db_BinaryMisc_Proxy.create(Db_BinaryMisc_Proxy.Type_BinaryDecoded, 4, '0' if cubin.no_decode else '1', 'This value is 1 if the binary is decoded, otherwise it is 0. Selective decoding is the default. Thus, usually one binary has this value set to 1 and the others to 0, at least in the beginning.'),
        ]
        return Db_Binary_Proxy.create(sass, 0, binary_name, db_kernel, [],  misc, 'The entry point to a decoded binary')

    @staticmethod
    def file_to_db(sass:SM_SASS, cubin:SM_CuBin_File) -> Db_Binary_Proxy:
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cubin, SM_CuBin_File): raise Exception(sp.CONST__ERROR_ILLEGAL)

        db_cubin:Db_Binary_Proxy = SM_Cubin_DB.file_to_db_partial(sass, cubin)
        bb_head:bytes =  cubin.bb_head
        bb_tail:bytes = cubin.bb_tail
        db_bb_head = Db_BinaryData_Proxy.create(Db_BinaryData_Proxy.Type_BinHead, 0, bb_head, 'The portion of the binary up until the Cuda bits start')
        db_bb_tail = Db_BinaryData_Proxy.create(Db_BinaryData_Proxy.Type_BinHead, 4, bb_tail, 'The portion of the binary from the end of the Cuda bits to the end of the binary')
        db_cubin.add_binary_data([db_bb_head, db_bb_tail])
        return db_cubin
    