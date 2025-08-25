#!/usr/bin/env python3

import sys

import typing
import pickle
import gzip
import struct
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from py_sass import SM_SASS
from py_sass import SASS_Class
from py_sass_ext import SASS_Enc_Dom
from . import _config as sp
from ._instr_cubin_repr import Instr_CuBin_Repr
from ._instr_cubin import Instr_CuBin
from ._instr_cubin_db_proxy import Db_Binary_Proxy
from .sm_cubin_lib import SM_CuBin_Lib
from .sm_cubin_kernel import SM_CuBin_Kernel
from .sm_cubin_file import SM_CuBin_File, SM_Cubin_Unloaded_Cache_Exception
from .sm_cubin_db import SM_Cubin_DB

###############################################################################
# gedit /home/$USER/.bashrc
# => add the following line:
# export PATH="...path-to-smd.py...:$PATH"
# => add exec rights: chmod +x smd.py
# source /home/lol/.venvs/standard/bin/activate && python3 ./py_sass/sm_cubin_service.py
###############################################################################

HOST_NAME = "localhost"
SERVER_PORT = 8180

class CORSHandler(BaseHTTPRequestHandler):
    def send_response(self, *args, **kwargs):
        BaseHTTPRequestHandler.send_response(self, *args, **kwargs)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')

class Sm_CuBin_Service(CORSHandler):
    __SM_CACHE:dict = dict()
    __SM_CACHE_DUMP:dict = dict()
    __KERNEL_CACHE = dict()
    
    # These ones serve to make the kernels selectively loadable
    __FF:typing.Dict[str, SM_CuBin_File] = dict()
    __U_BITS:typing.Dict[str, bytes] = dict()
    __PATHS:typing.Dict[str, str] = dict()

    @staticmethod
    def preload_all_sm(sms:list):
        for args in sms:
            sm = args[0]
            print("Pre-Load SM {0} into cache".format(sm))
            Sm_CuBin_Service.__SM_CACHE[sm] = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False, web_crawl=False)
            print("Store compressed SM {0} into cache".format(sm))
            Sm_CuBin_Service.__SM_CACHE_DUMP[sm] = gzip.compress(pickle.dumps(Sm_CuBin_Service.__SM_CACHE[sm]))
            if 'E' in args:
                print("Pre-Load EncDom {0} into cache".format(sm))
                Sm_CuBin_Service.__SM_CACHE[sm].load_encdom(show_progress=True)
            elif 'S' in args:
                print("Pre-Load small EncDom {0} into cache".format(sm))
                Sm_CuBin_Service.__SM_CACHE[sm].load_encdom_small(show_progress=True)

    def do_GET(self):
        parts = [i for i in self.path.split('/') if i]
        if parts[0] == 'testbin':
            location = os.path.dirname(os.path.realpath(__file__))
            fn = location + "/test_bins/" + "_".join(parts) + ".bin"
            try:
                with open(fn, 'rb') as f:
                    bb = f.read()
            except FileNotFoundError:
                self.send_response(404, "Requested test architecture [{}] not found!".format(parts[1]))
                return

            db_stream:bytes = self.decode_to_db_test("/test_bins", "_".join(parts), bb)

            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.send_header("Content-Transfer-Encoding", "binary")
            self.send_header("Content-Length", str(len(db_stream)))
            self.end_headers()
            self.wfile.write(db_stream)
            self.end_headers()
            return
        self.send_response(404, "Requested test [{0}] not found!".format(self.path))

    def do_POST(self):
        ll_tot = int(self.headers['content-length'])
        line = self.rfile.read(ll_tot)
        to_terminal = line[0] == 1
        to_html = line[0] == 2
        to_offline_html = line[0] == 3
        to_offline_db = line[0] == 50
        enc_dom_request = line[0] == 100
        sass_request = line[0] == 200
        lookup_db = line[0] == 99

        if to_terminal or to_html or to_offline_html: raise Exception('[!!! == DEPRECATED == !!!]')

        # if to_html or to_terminal or to_offline_html:
        #     res = self.decode(to_terminal, to_html, to_offline_html, line[1:])
        #     self.send_response(200)
        #     self.send_header("Content-type", "text/html")
        #     self.send_header("Content-Length", str(len(res)))
        #     self.end_headers()
        #     self.wfile.write(res.encode('utf-8'))
        if to_offline_db:
            res:bytes = self.decode_to_db(line[1:])
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
        elif enc_dom_request:
            i=1
            sm_nr = struct.unpack('!i', line[i:(i+4)])[0]
            i+=4
            class_name_l = struct.unpack('!i', line[i:(i+4)])[0]
            i+=4
            class_name = line[i:(i+class_name_l)].decode('utf-8')
            i+=class_name_l
            anker_len = struct.unpack('!i', line[i:(i+4)])[0]
            i+=4
            anker_b = line[i:(i+anker_len)]
            if len(anker_b) != anker_len: raise Exception(sp.CONST__ERROR_ILLEGAL)
            i+=anker_len
            exceptions_len = struct.unpack('!i', line[i:(i+4)])[0]
            i+=4
            exceptions_b = line[i:]
            if len(exceptions_b) != exceptions_len: raise Exception(sp.CONST__ERROR_ILLEGAL)
            
            # if we don't pass any ankers or exeptions, just use the regular pick method
            if anker_len == 0 and exceptions_len == 0:
                sass:SM_SASS = self.__SM_CACHE[sm_nr]
                encdom:SASS_Enc_Dom = sass.encdom
                enc_vals = encdom.pick(class_name)
            else:
                ankers = SM_CuBin_Lib.bytes_to_args(anker_b)
                exceptions = SM_CuBin_Lib.bytes_to_args(exceptions_b)
                sass:SM_SASS = self.__SM_CACHE[sm_nr]
                cc:SASS_Class = sass.sm.classes_dict[class_name]
                encdom:SASS_Enc_Dom = sass.encdom
                encdom.fix(class_name, ankers, exceptions)
                enc_vals = next(encdom.fixed_iter(class_name))
            bits = Instr_CuBin.instr_assemble_to_bv(sass, class_name, enc_vals)

            res = b''.join(b'1' if i else b'0' for i in bits)
            res += b':'
            res += SM_CuBin_Lib.args_to_bytes({k:{v} for k,v in enc_vals.items()})
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
        elif sass_request:
            sm_nr = struct.unpack('!i', line[1:5])[0]
            if not sm_nr in Sm_CuBin_Service.__SM_CACHE_DUMP:
                Sm_CuBin_Service.__SM_CACHE[sm_nr] = SM_SASS(sm_nr, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False, web_crawl=False)
                Sm_CuBin_Service.__SM_CACHE_DUMP[sm_nr] = gzip.compress(pickle.dumps(Sm_CuBin_Service.__SM_CACHE[sm_nr]))
            res = Sm_CuBin_Service.__SM_CACHE_DUMP[sm_nr]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
        elif lookup_db:
            res:bytes = SM_SASS.get_lookup_db()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
        else:
            raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        #     id = line.decode()
        #     s = id.rfind('-')
        #     k_id = id[:s]
        #     i_id = int(id[(s+1):])
        #     k:SM_CuBin_Kernel = Sm_CuBin_Service.__KERNEL_CACHE[k_id]
        #     b = k.get_body_html(self.__SM_CACHE[k.arch], i_id)

        #     self.send_response(200)
        #     self.send_header("Content-type", "text/html")
        #     self.send_header("Content-Length", str(len(b)))
        #     self.end_headers()
        #     self.wfile.write(json.dumps(b).encode('utf-8'))
            
    @staticmethod
    def decode_bit_stream(bits:bytes) -> typing.List[typing.Dict]:
        is_init:bool = (bits[0] == 1)
        load_mode = bits[1]

        i=2
        binaryNameLen = struct.unpack('!I', bits[i:(i+4)])[0]
        i+=4

        if is_init and binaryNameLen != 0: raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        if binaryNameLen > 0:
            binaryName = bits[i:(i+binaryNameLen)].decode('utf-8')
        else:
            binaryName = ""
        i+= binaryNameLen

        kernelNameLen = struct.unpack('!I', bits[i:(i+4)])[0]
        i+=4
        if is_init and kernelNameLen != 0: raise Exception(sp.CONST__ERROR_ILLEGAL)

        if kernelNameLen > 0:
            kernelName = bits[i:(i+kernelNameLen)].decode('utf-8')
        else:
            kernelName = ""
        i+=kernelNameLen
        
        bb:list = []
        while i < len(bits):
            l_path = struct.unpack('!I', bits[i:(i+4)])[0]
            i+=4
            b_path = bits[i:(i+l_path)]
            i+=l_path
            l_name = struct.unpack('!I', bits[i:(i+4)])[0]
            i+=4
            b_name = bits[i:(i+l_name)]
            i+=l_name
            ll = struct.unpack('!I', bits[i:(i+4)])[0]
            i+=4
            bb.append({
                'is_init': is_init,
                'load_mode': load_mode,
                'kernel_name': kernelName,
                'binary_name': binaryName,
                'path': b_path.decode('utf-8'),
                'name': b_name.decode('utf-8'),
                'bits': gzip.decompress(bits[i:(i+ll)]),
                'enc_bits_len': ll
            })
            i+=ll

        if not bb:
            if is_init: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            bb.append({
                'is_init': is_init,
                'load_mode': load_mode,
                'kernel_name': kernelName,
                'binary_name': binaryName,
                'path': '',
                'name': '',
                'bits': '',
                'enc_bits_len': 0
            })
        return bb

    def decode_to_db_test(self, path:str, name:str, u_bits:bytes) -> bytes:
        ff:SM_CuBin_File
        try:
            ff:SM_CuBin_File = SM_CuBin_File(self.__SM_CACHE, u_bits)
            ff.overwrite_location(path)
            ff.overwrite_name(name)
        except SM_Cubin_Unloaded_Cache_Exception:
            arch = SM_CuBin_File.cur_sm_nr
            print("Load SM {0} into cache".format(arch))
            Sm_CuBin_Service.__SM_CACHE[arch] = SM_SASS(arch)
            Sm_CuBin_Service.__SM_CACHE_DUMP[arch] = gzip.compress(pickle.dumps(Sm_CuBin_Service.__SM_CACHE[arch]))
            
            # Try again...
            ff:SM_CuBin_File = SM_CuBin_File(self.__SM_CACHE, u_bits)

        arch = ff.sm_nr
        db:Db_Binary_Proxy = SM_Cubin_DB.file_to_db(Sm_CuBin_Service.__SM_CACHE[arch], ff)

        db_con = SM_Cubin_DB.persist_bins([db])
        compressed_b_stream:bytes = SM_Cubin_DB.db_con_to_mem(db_con, compress=False)
        return compressed_b_stream

    def decode_to_db(self, bits:bytes) -> bytes:
        bb = Sm_CuBin_Service.decode_bit_stream(bits)

        is_init:bool = bb[0]['is_init']
        all_db = []
        if is_init:
            # print("[DEBUG...] init load")
            # purge the cache
            Sm_CuBin_Service.__FF = dict()
            Sm_CuBin_Service.__U_BITS = dict()
            Sm_CuBin_Service.__PATHS = dict()

            # sort by binary name
            bb = sorted(bb, key=lambda x:x['name'])
            for b_ind,b in enumerate(bb):
                is_init = b['is_init']
                load_mode = b['load_mode']
                kernel_name = b['kernel_name']
                binary_name = b['binary_name']
                u_bits = b['bits']
                path = b['path']
                name = b['name']

                ff:SM_CuBin_File
                if load_mode == 1:
                    # This one automatically only loads the first kernel of all the binaries we get
                    try:
                        # print("[DEBUG...] Load first kernel")
                        ff:SM_CuBin_File = SM_CuBin_File(self.__SM_CACHE, u_bits, selected_kernel='.', no_decode=True if b_ind > 0 else False)
                        ff.overwrite_location(path)
                        ff.overwrite_name(name)
                    except SM_Cubin_Unloaded_Cache_Exception:
                        # NOTE: this mechanism really doesn't work properly...
                        arch = SM_CuBin_File.cur_sm_nr
                        print("Load SM {0} into cache".format(arch))
                        Sm_CuBin_Service.__SM_CACHE[arch] = SM_SASS(arch)
                        Sm_CuBin_Service.__SM_CACHE_DUMP[arch] = gzip.compress(pickle.dumps(Sm_CuBin_Service.__SM_CACHE[arch]))
                        
                        # Try again...
                        ff:SM_CuBin_File = SM_CuBin_File(self.__SM_CACHE, u_bits, selected_kernel='.', no_decode=True if b_ind > 0 else False)
                elif load_mode == 2:
                    # This one loads all the kernels
                    try:
                        # print("[DEBUG...] Load all kernels")
                        ff:SM_CuBin_File = SM_CuBin_File(self.__SM_CACHE, u_bits, selected_kernel='')
                        ff.overwrite_location(path)
                        ff.overwrite_name(name)
                    except SM_Cubin_Unloaded_Cache_Exception:
                        # NOTE: this mechanism really doesn't work properly...
                        arch = SM_CuBin_File.cur_sm_nr
                        print("Load SM {0} into cache".format(arch))
                        Sm_CuBin_Service.__SM_CACHE[arch] = SM_SASS(arch)
                        Sm_CuBin_Service.__SM_CACHE_DUMP[arch] = gzip.compress(pickle.dumps(Sm_CuBin_Service.__SM_CACHE[arch]))
                        
                        # Try again...
                        ff:SM_CuBin_File = SM_CuBin_File(self.__SM_CACHE, u_bits, selected_kernel='')
                
                Sm_CuBin_Service.__FF[name] = ff
                Sm_CuBin_Service.__U_BITS[name] = u_bits
                Sm_CuBin_Service.__PATHS[name] = path

                arch = ff.sm_nr
                db:Db_Binary_Proxy = SM_Cubin_DB.file_to_db(Sm_CuBin_Service.__SM_CACHE[arch], ff)
                all_db.append(db)
        else:
            # print("[DEBUG...] NOT init load")
            if not len(bb) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if not bb[0]['bits'] == '': raise Exception(sp.CONST__ERROR_ILLEGAL)
            if not bb[0]['path'] == '': raise Exception(sp.CONST__ERROR_ILLEGAL)
            if not bb[0]['name'] == '': raise Exception(sp.CONST__ERROR_ILLEGAL)
            if not bb[0]['enc_bits_len'] == 0: raise Exception(sp.CONST__ERROR_ILLEGAL)

            load_mode:int = bb[0]['load_mode']
            kernel_name:str = bb[0]['kernel_name']
            binary_name:str = bb[0]['binary_name']

            # this one already has a some kernels loaded
            if not (binary_name != ""): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if(not Sm_CuBin_Service.__FF): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if not (binary_name in Sm_CuBin_Service.__FF): raise Exception(sp.CONST__ERROR_UNEXPECTED)

            for name,u_bits in Sm_CuBin_Service.__U_BITS.items():
                if load_mode == 1:
                    if name == binary_name:
                        # print("[DEBUG...] later on, load selective kernel", name)
                        # This one selectively loads the new kernel 'kernel_name'. If we don't have a kernel name
                        # default to the first one again. This happens if the user has multiple binaries loaded and changes the binary.
                        if kernel_name == "": kernel_name = '.'
                        # Make sure we will decode this file
                        ff:SM_CuBin_File = Sm_CuBin_Service.__FF[name]
                        ff.set_no_decode(False)
                        ff.continue_file_decoding(self.__SM_CACHE[ff.sm_nr], kernel_name)
                    else:
                        ff:SM_CuBin_File = Sm_CuBin_Service.__FF[name]
                        ff.set_no_decode(True)
                elif load_mode == 2:
                    # print("[DEBUG...] later on, load all missing kernels")
                    # This one loads the entire binary kernel
                    ff:SM_CuBin_File = Sm_CuBin_Service.__FF[name]
                    ff.continue_file_decoding(self.__SM_CACHE[ff.sm_nr], selected_kernel='')
                else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                

                arch = ff.sm_nr
                db:Db_Binary_Proxy = SM_Cubin_DB.file_to_db(Sm_CuBin_Service.__SM_CACHE[arch], ff)
                all_db.append(db)
            
        db_con = SM_Cubin_DB.persist_bins(all_db)
        compressed_b_stream:bytes = SM_Cubin_DB.db_con_to_mem(db_con, compress=True)
        return compressed_b_stream

    # def decode(self, to_terminal:bool, to_html:bool, to_offline_html:bool, bits:bytes):
    #     bin_start_offset_hex = '0x' + bits[0:8].decode('utf-8')
    #     bin_end_offset_hex = '0x' + bits[8:16].decode('utf-8')

    #     bits = bits[16:]
    #     is_blackwell = int(bits[8]) == 8

    #     # Get integer that designates which architecture we are on
    #     arch = SM_CuBin_Lib.read_arch(is_blackwell, bits)

    #     if not arch in self.__SM_CACHE:
    #         print("Load SM {0} into cache".format(arch))
    #         Sm_CuBin_Service.__SM_CACHE[arch] = SM_SASS(arch)
    #         Sm_CuBin_Service.__SM_CACHE_DUMP[arch] = gzip.compress(pickle.dumps(Sm_CuBin_Service.__SM_CACHE[arch]))

    #     head, all_id, all_kernel, tail = SM_CuBin_Kernel.init_kernel_kk(self.__SM_CACHE[arch], arch, bin_start_offset_hex, bin_end_offset_hex, bits, not to_offline_html)
    #     new = {id:kk for id,kk in zip(all_id, all_kernel)}
    #     Sm_CuBin_Service.__KERNEL_CACHE |= new
    #     return self.construct_reply(self.__SM_CACHE[arch], new, to_terminal, to_html, to_offline_html, arch)

    # @staticmethod
    # def construct_reply(sass:SM_SASS, kernel:dict, to_terminal:bool, to_html:bool, to_offline_html:bool, arch:int):
    #     if to_terminal: return Sm_CuBin_Service.construct_terminal(sass, kernel, arch)
    #     elif to_html or to_offline_html: return Sm_CuBin_Service.construct_html(sass, kernel, arch, to_offline_html)
    #     else: return Sm_CuBin_Service.construct_file(sass, kernel, arch)

    # @staticmethod
    # def construct_file(sass:SM_SASS, kernel:typing.List[SM_CuBin_Kernel], arch:int):
    #     raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

    # @staticmethod
    # def construct_terminal(sass:SM_SASS, kernel:typing.List[SM_CuBin_Kernel], arch:int):
    #     raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    
    @staticmethod
    def construct_db(sass:SM_SASS, kernel:typing.Dict[str,SM_CuBin_Kernel], arch:int):
        db_vals = []
        for kk in kernel.values():
            u:Instr_CuBin_Repr
            for u in kk.universes:
                db_vals.append(u.to_db(sass))
        
        return db_vals
    
    # @staticmethod
    # def construct_html(sass:SM_SASS, kernel:typing.Dict[str,SM_CuBin_Kernel], arch:int, to_offline_html:bool, test_run=False):
    #     raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        # html_main_body = []
        # for kk in kernel.values():
        #     html = []
        #     nn = kk.kernel_name + "." + str(arch)
            
        #     ll_cn = len(kk.universes)
        #     u:Instr_CuBin_Repr
        #     for u in kk.universes:
        #         if to_offline_html: html.append(u.to_offline_html(ll_cn, sass))
        #         else: html.append(u.to_html_head(ll_cn, sass))

        #     # If we have a test_run, we may accumulate millions of instructions
        #     # and we only care to test if the calculations work, not how they look
        #     if not test_run: html_main_body.append(Instr_CuBin_Html.kernel(nn, "".join(html)))
        
        # return Instr_CuBin_Html.main_body("".join(html_main_body), to_offline_html, HOST_NAME, SERVER_PORT)

    @staticmethod
    def main(sms:list, preload:bool):
        # sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90, 100, 120]
        if preload:
            Sm_CuBin_Service.preload_all_sm(sms)

        webServer = HTTPServer((HOST_NAME, SERVER_PORT), Sm_CuBin_Service)
        print("Server started http://%s:%s" % (HOST_NAME, SERVER_PORT))

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()
        print("Server stopped.")

def py_cubin_smd_service():
    if len(sys.argv) == 1:
        Sm_CuBin_Service.main([], False)
    else:
        sms = [tuple(int(j) if ind == 0 else j for ind,j in enumerate(i.strip().split('.'))) for i in " ".join(sys.argv[1:])[1:-1].split(',')]
        Sm_CuBin_Service.main(sms, True if sms else False)
