#!/usr/bin/env python3

import os
import typing
import sqlite3
import pickle
import datetime
import sys
import copy
import requests
import gzip
import struct
import termcolor as tc
from . import _config as sp
from py_sass import SM_SASS
from py_sass_ext import BitVector
from .sm_cubin_lib import SM_CuBin_Lib
from ._instr_cubin_test import Instr_CuBin_Test
from ._instr_cubin import CubinDecodeException, Instr_CuBin
from .sm_cubin_db import SM_Cubin_DB
from .sm_cubin_service import Sm_CuBin_Service
from .sm_cubin_file import SM_CuBin_File
from .sm_cubin_elf import SM_Cubin_Elf
from .sm_cubin_utils import SM_CuBin_Utils

###############################################################################
# gedit /home/$USER/.bashrc
# => add the following line:
# export PATH="...path-to-smd.py...:$PATH"
# => add exec rights: chmod +x smd.py
# source /home/lol/.venvs/standard/bin/activate
###############################################################################

class Py_SMD:
    def __init__(self, 
                 cubins:typing.List[str], ip:str, port:int, 
                 to_terminal:bool, to_html:bool, to_offline_html:bool, to_offline_db:bool, test:bool):
        
        url = "http://{ip}:{port}".format(ip=ip, port=port)
        
        # Set some flags
        # NOTE: to_html, to_offline_html and to_terminal are no longer used
        # if to_terminal: to_t = b"\x01" 
        # elif to_html: to_t = b"\x02" 
        # elif to_offline_html: to_t = b"\x03"
        if to_offline_db: to_t = b"\x32" # 50
        else: to_t = b"\x00"

        # Open all binaries and pack them into a byte stream
        l_bits:list = []
        llen = []
        llenc = []
        for cubin in cubins:
            if to_offline_db:
                with open(cubin, 'rb') as f:
                    bbits = f.read()
                # NOTE: in this case, we send the entire file as compressed gzip
                pp = cubin.split('/')
                path = "/".join(pp[:-1])
                name = pp[-1]
                llen.append(len(bbits))
                b_path = path.encode('utf-8')
                l_path = struct.pack('!I', len(b_path))
                b_name = name.encode('utf-8')
                l_name = struct.pack('!I', len(b_name))
                
                cbbits = gzip.compress(bbits)
                l = len(cbbits)
                llenc.append(l)
                lbytes = struct.pack('!I', l)
                l_bits.extend([l_path, b_path, l_name, b_name, lbytes, cbbits])
            else: raise Exception(sp.CONST__ERROR_ILLEGAL)

        bits = b''.join(l_bits)
        # If -test is passed as flag, this portion runs
        # NOTE: there is a 'return' at the end of this!
        if test:
            bb = Sm_CuBin_Service.decode_bit_stream(bits)
            sass_d = {86: SM_SASS(86), 80:SM_SASS(80), 75:SM_SASS(75)}
            all_ff = []
            for ind,b in enumerate(bb):
                b_bits = b['bits']
                b_name = b['name']
                b_path = b['path']
                enc_len = b['enc_bits_len']
                
                len1 = enc_len == llenc[ind]
                len2 = len(b_bits) == llen[ind]
                if not len1 and len2: raise Exception("Not good...")
                
                ff = SM_CuBin_File(sass_d, b_bits)
                ff.overwrite_location(b_path)
                ff.overwrite_name(b_name)
                all_ff.append(ff)
                pass

            bins = [SM_Cubin_DB.file_to_db(sass_d[86], all_ff[0]), SM_Cubin_DB.file_to_db(sass_d[80], all_ff[1]), SM_Cubin_DB.file_to_db(sass_d[75], all_ff[2])]
            db_con = SM_Cubin_DB.persist_bins(bins)
            SM_Cubin_DB.db_con_to_file(db_con, 'multi_test.db')
            return

        # Pass the byte stream to the server
        response:requests.Response = requests.post(url, data=to_t + bits)
        tt = datetime.datetime.now()
        # Formulate some file name that is somewhat unique and contains data and time of creation
        target_path = os.getcwd() + "/{0}.sass-dump." + tt.strftime("%d-%m-%Y_%H-%M-%S") + ".autogen.{1}"

        # DB is really the only one that counts...
        if to_offline_db:
            fn = target_path.format(cubins[0].split('/')[-1], "db")
            print("Save to [{0}]".format(tc.colored(fn, 'red')))
            # Perform backwards transformations from byte stream to db
            # NOTE: multiple binaries get packed into the same database (this is on purpose!)
            # NOTE: don't remove the compressed=True flag!
            db_con:sqlite3.Connection = SM_Cubin_DB.db_mem_to_con(response.content, compressed=True)
            SM_Cubin_DB.db_con_to_file(db_con, fn)
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)
    
    @staticmethod
    def parse_args(argv:list):
        msg = ''
        ip = 'localhost'
        port = 8180
        params = " ".join(argv)

        if not (params.find('[') >= 0 and params.find(']') >= 0): 
            msg = "Invalid params with no [...] specified: < {0} >".format(params)
            return msg, ip, port, set(), []
        pref, post = params.split('[', 1)
        p1 = pref.split(']')
        p2 = post.split(']')
        if len(p1) == 2 and len(p2) == 1:
            part1 = p1[0].strip()
            pargs = p1[1].strip()
            part3 = p2[0].strip()
        elif len(p2) == 2 and len(p1) == 1:
            part1 = p1[0].strip()
            pargs = p2[0].strip()
            part3 = p2[1].strip()
        else: 
            msg = "Invalid params: < {0} >".format(params)
            return msg, ip, port, set(), []

        a1 = part1.split()
        args = [a.strip() for a in pargs.split(',')]
        a2 = part3.split()

        def get_addr(xx:list, params:str, ip:str, port:int):
            ind = xx.index('-con')
            if not (len(xx) > (ind+1)): 
                msg = "Missing ip:port in params with [-con] specified: < {0} >".format(params)
                return msg, ind, '-', 0
            
            ip_port_str:str = xx[ind+1]
            ip_port:list = ip_port_str.split(':')
            if not len(ip_port) == 2: 
                msg = "Invalid ip:port address in params with [-con] specified: < {0} >".format(params)
                return msg, ind, ip, port
            
            ip = ip_port[0]
            port = int(ip_port[1])
            return '',ind,ip,port
        
        if '-con' in a1:
            msg,ind,ip,port = get_addr(a1, params, ip, port)
            if not msg:
                del a1[ind]
                del a1[ind]
        elif '-con' in a2:
            msg,ind,ip,port = get_addr(a2, params, ip, port)
            if not msg:
                del a2[ind]
                del a2[ind]

        if not msg: funcs = set(a1[1:] + a2)
        else: funcs = set()

        return msg,ip,port,funcs,args

    @staticmethod
    def main(argv:list):
        to_terminal = False
        to_html = False
        to_offline_html = False
        to_offline_db = True
        to_file = False
        to_all = False

        # Some explanatory message
        msg = ''
        msg += "Specify input files as list: [....] using complete or relative, valid path starting at least with './'\n"
        msg += "Specify functions:\n"
        msg += " -fall: convert complete binary to .hex file\n"
        msg += " -fcubin: convert Cuda portion of binary to .hex file\n"
        msg += " -odb: convert complete binary to .db file\n"
        msg += " -test: run .db conversion locally\n" 
        msg += "       NOTE: this is just a flag to isolate portions of the code.\n" 
        msg += "             The code may have to be adapted for a suitable testcase.\n"
        msg += "Specify connection if it's not the standard [127.0.0.1:8180]\n"
        msg += " - con ip:port\n"
        msg += "For example:\n"
        msg += '-fall -fcubin -odb -con 127.1.2.3:8180 [./experiment.rqwr.template_86, ./experiment.rqwr.template_80,./experiment.rqwr.template_120]\n'
        msg += "  => convert given three files to .hex twice and convert to .db and connect to 127.1.2.3, port 8180\n"
        msg += '-odb [./experiment.rqwr.template_86]\n'
        msg += '  => convert given file to .db and connect to standard address'
        
        # If we pass -help, show the message
        if argv[1] == '-help':
            print(tc.colored('====================================================================','green'))
            print(msg)
            print(tc.colored('====================================================================','green'))
            return

        # ret_msg != '' => some sort of error in decoding => show the message too
        ret_msg,ip,port,funcs,args = Py_SMD.parse_args(argv)
        if ret_msg:
            print(tc.colored("[ERROR]", 'red', attrs=['bold']))
            print(tc.colored('====================================================================', 'red'))
            print(tc.colored(ret_msg, 'red'))
            print(tc.colored('====================================================================', 'red'))
            print(tc.colored(msg, 'green'))
            print(tc.colored('====================================================================','green'))
            return

        # to_terminal = True if sys.argv[1] == '-t' else False
        # to_html = True if '-html' in funcs else False
        # to_offline_html = True if '-ohtml' in funcs else False
        to_offline_db = True if '-odb' in funcs else False
        to_file = True if '-fcubin' in funcs else False
        to_all = True if '-fall' in funcs else False
        test = True if '-test' in funcs else False

        # if to_terminal or to_html or to_offline_html:
        #     raise Exception('[DEPRECATED]: use [-odb] instead of [-ohtml, -html]')
        
        # Perform all registered functions
        # NOTE: no if-elif-else => allow multiple functions at once
        if to_offline_db:
            Py_SMD(args, ip, port, False, False, False, to_offline_db, test)
        if to_file:
            FILE(args)
        if to_all:
            FILE_ALL(args)

class FILE:
    def __init__(self, cubins:typing.List[str]):
        for cubin in cubins:
            res = SM_CuBin_Lib.read_ncod_full(cubin)
            path = res['pp']
            k_bits:bytes = res['kk'] # type: ignore
            k_start = res['is']
            k_end = res['ie']
            all_bits = res['bb']
            cuda_arch = res['sm']

            is_blackwell = int(k_bits[8]) == 8

            # Get integer that designates which architecture we are on
            arch = SM_CuBin_Lib.read_arch(is_blackwell, k_bits)
            words = SM_CuBin_Lib.bits_to_words(k_bits)
            tt = datetime.datetime.now()
            hex_file = cubin + "." + tt.strftime("%d-%m-%Y_%H-%M-%S") + ".autogen." + str(arch) + ".hex"
            hex_file_elf = cubin + "." + tt.strftime("%d-%m-%Y_%H-%M-%S") + ".autogen." + str(arch) + ".elf.hex"

            elf = SM_Cubin_Elf(arch, k_bits)
            elf_words = SM_CuBin_Lib.bits_to_words(elf.to_exec())

            # This is a test
            if not words == elf_words:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

            with open(hex_file,'w') as f:
                f.write("\n".join(["0x" + hex(ind*8)[2:].zfill(len(str(len(words)))) + ": " + " ".join([ww.upper() for ww in w]) for ind,w in enumerate(words)]))
            with open(hex_file_elf,'w') as f:
                f.write("\n".join(["0x" + hex(ind*8)[2:].zfill(len(str(len(elf_words)))) + ": " + " ".join([ww.upper() for ww in w]) for ind,w in enumerate(elf_words)]))

class FILE_ALL:
    def __init__(self, cubins:typing.List[str]):
        for cubin in cubins:
            res = SM_CuBin_Lib.read_ncod_full(cubin)
            k_bits:bytes = res['kk'] # type: ignore
            k_start:int = res['is'] # type: ignore
            k_end:int = res['ie'] # type: ignore
            all_bits:bytes = res['bb'] # type: ignore

            is_blackwell = int(k_bits[8]) == 8

            # Get integer that designates which architecture we are on
            arch = SM_CuBin_Lib.read_arch(is_blackwell, k_bits)
            words = SM_CuBin_Lib.bits_to_words(all_bits)
            tt = datetime.datetime.now()
            hex_file = cubin + "." + tt.strftime("%d-%m-%Y_%H-%M-%S") + ".all.autogen." + str(arch) + ".hex"

            with open(hex_file,'w') as f:
                f.write('arch: {0}\n'.format(arch))
                f.write('k_start: {0}\n'.format(hex(k_start)))
                f.write('k_end: {0}\n'.format(hex(k_end)))
                f.write("\n".join(["0x" + hex(ind*8)[2:].zfill(len(str(len(words)))) + ": " + " ".join([ww.upper() for ww in w]) for ind,w in enumerate(words)]))

def py_smd():
    Py_SMD.main(sys.argv)

def py_test_encdec():
    location = '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates'

    # location = os.path.dirname(os.path.realpath(__file__))
    # pp = location + "/DocumentSASS/sm_{0}_domains.lz4"
    # args = " ".join(sys.argv[1:])
    # sm_args, cc = args.split(']')
    # sms = [tuple(int(j) if ind == 0 else j for ind,j in enumerate(i.strip().split('.'))) for i in " ".join(sys.argv[1:])[1:-1].split(',')]
    # sms = [50, 52, 53, 60, 61, 62]
    # sms = [70, 72]
    sms = [86]
    # sms = [90]
    # sms = [100]
    # sms = [120]
    single_class = False
    single_class_name:str = 'al2p__RaNonRZ'
    for sm in sms:
        sass:SM_SASS
        sass = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)

        sass.load_encdom(show_progress=True)
        Instr_CuBin_Test.test_instr_enc(sass, 2, single_class, single_class_name, p_step=250)

        # Instr_CuBin_Test.test_cubin_decode(sass, '{0}/experiment.mc.template_{1}'.format(location, sm))
        # Instr_CuBin.test_instr_enc_iter(sass, single_class, single_class_name, p_step=250)

def py_test_to_exec():
    location = '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates'
    # kkm6 = '{0}/experiment.mc.template_{1}'.format(location, 50)
    # kkm5 = '{0}/experiment.mc.template_{1}'.format(location, 52)
    # kkm4 = '{0}/experiment.mc.template_{1}'.format(location, 53)
    # kkm3 = '{0}/experiment.mc.template_{1}'.format(location, 60)
    # kkm2 = '{0}/experiment.mc.template_{1}'.format(location, 61)
    # kkm1 = '{0}/experiment.mc.template_{1}'.format(location, 62)
    kk0 = '{0}/experiment.mc.template_{1}'.format(location, 70)
    kk1 = '{0}/experiment.mc.template_{1}'.format(location, 72)
    kk2 = '{0}/experiment.mc.template_{1}'.format(location, 75)
    kk3 = '{0}/experiment.mc.template_{1}'.format(location, 80)
    kk4 = '{0}/experiment.mc.template_{1}'.format(location, 86)
    kk5 = '{0}/experiment.mc.template_{1}'.format(location, 90)
    kk6 = '{0}/experiment.mc.template_{1}'.format(location, 100)
    kk7 = '{0}/experiment.mc.template_{1}'.format(location, 120)
    # args = '-odb [{0}] -con 127.0.0.1:8180'.format(kk1,kk2,kk3).split()
    # # args = '-fall -fcubin  -odb -con 127.0.0.1:8180 [./experiment.rqwr.template_86, ./experiment.rqwr.template_80,./experiment.rqwr.template_120'.split()
    # sys.argv.extend(args)
    # FILE([kkm6, kkm5, kkm4, kkm3, kkm2, kkm1, kk0, kk1, kk2, kk3, kk4, kk5, kk6, kk7])
    # FILE([kk6, kk7])

    sass = dict()
    url = "http://{ip}:{port}".format(ip='127.0.0.1', port=8180)

    location = '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/fixed_latency_instructions/binaries'
    sm = 86
    kk8 = '{0}/sw_2.{1}'.format(location, sm)
    kk9 = '{0}/sw_4.{1}'.format(location, sm)
    for kk in [kk8, kk9]:
        print("... test {0}".format(kk))
        if not sm in sass:
            data = b'\xc8' + struct.pack('!i', sm)
            response = requests.post(url=url, data=data)
            sass[sm] = pickle.loads(gzip.decompress(response.content))
            # sass[sm] = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
        try:
            ff1 = SM_CuBin_File(sass[sm], kk)
            ff1.to_exec("{0}/test.autogen".format(location), test_run=True)
        except CubinDecodeException as error:
            if sm in [70,72]:
                if not 75 in sass:
                    data = b'\xc8' + struct.pack('!i', 75)
                    response = requests.post(url=url, data=data)
                    sass[75] = pickle.loads(gzip.decompress(response.content))
                    # sass[75] = SM_SASS(75, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
                ff1 = SM_CuBin_File(sass[75], kk)

    for sm,kk in zip([70,72,75,80,86,90,100,120],[kk0,kk1,kk2,kk3,kk4,kk5,kk6,kk7]):
        print("... test {0}".format(kk))
        if not sm in sass:
            data = b'\xc8' + struct.pack('!i', sm)
            response = requests.post(url=url, data=data)
            sass[sm] = pickle.loads(gzip.decompress(response.content))
            # sass[sm] = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
        try:
            ff1 = SM_CuBin_File(sass[sm], kk)
            ff1.to_exec("{0}/test.autogen".format(location), test_run=True)
        except CubinDecodeException as error:
            if sm in [70,72]:
                if not 75 in sass:
                    data = b'\xc8' + struct.pack('!i', 75)
                    response = requests.post(url=url, data=data)
                    sass[75] = pickle.loads(gzip.decompress(response.content))
                    # sass[75] = SM_SASS(75, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
                ff1 = SM_CuBin_File(sass[75], kk)
    
    # Select the files that should be binaries and are either .mod or not
    # Select the files with SM 70++

    files = [x for x in [(int(i.split('.')[-1]) if not i.endswith('.mod') else int(i.split('.')[-2]), location + "/" + i) for i in os.listdir(location) if not (i.endswith('.result') or i.find('autogen') >= 0)] if x[0]>=70]
    for sm,kk in files:
        print("... test {0}".format(kk))
        if not sm in sass:
            data = b'\xc8' + struct.pack('!i', sm)
            response = requests.post(url=url, data=data)
            sass[sm] = pickle.loads(gzip.decompress(response.content))
            # sass[sm] = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
        try:
            ff1 = SM_CuBin_File(sass[sm], kk)
            ff1.to_exec("{0}/test.autogen".format(location), test_run=True)
        except CubinDecodeException as error:
            if sm in [70,72]:
                if not 75 in sass:
                    data = b'\xc8' + struct.pack('!i', 75)
                    response = requests.post(url=url, data=data)
                    sass[75] = pickle.loads(gzip.decompress(response.content))
                    # sass[75] = SM_SASS(75, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
                ff1 = SM_CuBin_File(sass[75], kk)

    # sm = 75
    # sass[sm] = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
    # ff = SM_CuBin_File(sass[sm], '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/sw/binaries/sw_7.70')

    pass

def py_test_smd_parse():
    args1 = 'smd -odb [./experiment.rqwr.template_86, ./experiment.rqwr.template_80, ./experiment.rqwr.template_120] -con 127.0.0.1:8180'
    args2 = 'smd -con 127.0.0.1:8180 -odb [./experiment.rqwr.template_86, ./experiment.rqwr.template_80, ./experiment.rqwr.template_120]'
    args3 = 'smd -fall -fcubin  -odb -con 127.0.0.1:8180 [./experiment.rqwr.template_86, ./experiment.rqwr.template_80,./experiment.rqwr.template_120]'
    ret_msg,ip,port,funcs,args = Py_SMD.parse_args(args3.split())
    print(ret_msg,ip,port,funcs,args)
    ret_msg,ip,port,funcs,args = Py_SMD.parse_args(args1.split())
    print(ret_msg,ip,port,funcs,args)
    ret_msg,ip,port,funcs,args = Py_SMD.parse_args(args2.split())
    print(ret_msg,ip,port,funcs,args)
    args4 = 'smd -fall -fcubin  -odb -con [./experiment.rqwr.template_86, ./experiment.rqwr.template_80,./experiment.rqwr.template_120]'
    ret_msg,ip,port,funcs,args = Py_SMD.parse_args(args4.split())
    print(ret_msg,ip,port,funcs,args)
    args5 = 'smd -fall -fcubin  -odb -con 127.0.0.1:8180 ./experiment.rqwr.template_86, ./experiment.rqwr.template_80,./experiment.rqwr.template_120]'
    ret_msg,ip,port,funcs,args = Py_SMD.parse_args(args5.split())
    print(ret_msg,ip,port,funcs,args)
    args6 = 'smd -fall -fcubin  -odb -con 127.0.0.1:8180 [./experiment.rqwr.template_86, ./experiment.rqwr.template_80,./experiment.rqwr.template_120'
    ret_msg,ip,port,funcs,args = Py_SMD.parse_args(args6.split())
    print(ret_msg,ip,port,funcs,args)

    sys.argv.append('-help')
    Py_SMD.main(sys.argv)

def py_calc_nops():
    # sm = 100
    all_nops = dict()
    all_bits = dict()
    all_words = dict()
    for sm in [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90, 100, 120]:
    # for sm in [86]:
        sass = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
        sass.load_encdom_small()

        if sm <= 62:
            class_name = 'NOP'
            enc_vals = sass.encdom.pick(instr_class=class_name)
            enc_vals = SM_CuBin_Utils.overwrite_helper(0x0, 'uImm', enc_vals)
            enc_vals = SM_CuBin_Utils.overwrite_helper(15, 'Test', enc_vals)
            enc_vals = SM_CuBin_Utils.overwrite_helper(0x0, 'usched_info', enc_vals)
            print(SM_CuBin_Utils.enc_vals_dict_to_init(enc_vals))
            bits = Instr_CuBin.instr_assemble_to_bv(sass, class_name, enc_vals)
            bwords = Instr_CuBin.instr_bv_list_to_bwords(sass, [bits, bits, bits])
            instr_bytes = Instr_CuBin.instr_bwords_to_bytes(bwords)
        else:
            class_name = 'nop_'
            enc_vals = sass.encdom.pick(instr_class=class_name)
            enc_vals = SM_CuBin_Utils.overwrite_helper(0x0, 'usched_info', enc_vals)
            print(SM_CuBin_Utils.enc_vals_dict_to_init(enc_vals))
            bits = Instr_CuBin.instr_assemble_to_bv(sass, class_name, enc_vals)
            bwords = Instr_CuBin.instr_bv_list_to_bwords(sass, [bits])
            instr_bytes = Instr_CuBin.instr_bwords_to_bytes(bwords)
        
        all_bits[sm] = bits
        all_nops[sm] = instr_bytes
        all_words[sm] = bwords

    pass

def py_test_to_file():
    # sm = 100
    # for sm in [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90, 100, 120]:
    # for sm in [70, 72, 75, 80, 86, 90, 100, 120]:
    for sm in [86]:
        ff = '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/nogit__proj/benchmark_binaries_86/sust_d_imm__0_86'
        location = '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/04_Benchmark/build'
        ff = '{0}/mc.template_{1}'.format(location, sm)

        ff = '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/nogit__non_mem_86/non_mem.0.bin'
        sass = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
        ff1 = SM_CuBin_File(sass, ff, wipe=True)

        pass

        # print("SM {0} =======================".format(sm))
        # location = '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/modified_binaries'
        # kk1 = '{0}/template.{1}.mod'.format(location, sm)
        # kk1_new = '{0}/template.autogen.{1}'.format(location, sm)
        # location = '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates/'
        # kk2 = '{0}/experiment.mc.template_{1}'.format(location, sm)
        # kk2_new = '{0}/experiment.mc.template.autogen.{1}'.format(location, sm)

        # # args = '-odb [{0}] -con 127.0.0.1:8180'.format(kk1,kk2,kk3).split()
        # # # args = '-fall -fcubin  -odb -con 127.0.0.1:8180 [./experiment.rqwr.template_86, ./experiment.rqwr.template_80,./experiment.rqwr.template_120'.split()
        # # sys.argv.extend(args)
        # # FILE([kkm6, kkm5, kkm4, kkm3, kkm2, kkm1, kk0, kk1, kk2, kk3, kk4, kk5, kk6, kk7])
        # # FILE([kk6, kk7])

        # sass = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False)
        # ff1 = SM_CuBin_File(sass, kk1)
        # ff1c = copy.copy(ff1)

        # ff2 = SM_CuBin_File(sass, kk2)

    dd1 = SM_Cubin_DB.file_to_db(sass, ff1)
    # dd2 = SM_Cubin_DB.file_to_db(sass, ff2)

    # db_con = SM_Cubin_DB.persist_bins([dd1, dd2])
    # SM_Cubin_DB.db_con_to_file(db_con, "test_db_w_graph.db")




    # nrc = ff1.reg_count()
    # nnrc = {n:k+10 for n,k in nrc.items()}
    # ff1.overwrite_reg_count(nnrc)
    # ff1.to_exec(kk1_new)

    # nrc = ff2.reg_count()
    # nnrc = {n:k+10 for n,k in nrc.items()}
    # ff2.overwrite_reg_count(nnrc)
    # ff2.to_exec(kk2_new)
    pass

if __name__ == '__main__' or True:
    # py_test_encdec()
    # py_test_smd_parse()
    # py_test_to_exec()
    # py_calc_nops()
    # py_test_to_file()
    
    # SM_CuBin_File(sass, kk8)
    # SM_CuBin_File(sass, kk9)
    # FILE([kk1, kk2])

    # args = '-odb [{0}] -con 127.0.0.1:8180'.format(kk1,kk2,kk3).split()
    # args = '-fall -fcubin  -odb -con 127.0.0.1:8180 [./experiment.rqwr.template_86, ./experiment.rqwr.template_80,./experiment.rqwr.template_120'.split()
    # sys.argv.extend(args)

    from .sm_cubin_service import py_cubin_smd_service
    sys.argv.extend(['[', '75.S',']'])
    py_cubin_smd_service()
