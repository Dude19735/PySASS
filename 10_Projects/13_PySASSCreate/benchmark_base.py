import sys
import os
import typing
import shutil
import datetime
import json
import termcolor as tc
from multiprocessing import Process
from py_cubin import SM_CuBin_File
from py_sass_ext import SASS_Bits
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
import _config as sp
from helpers import Helpers
from kernel_output import KernelOutput
from control_props import ControlProps
from binstr_base import BInstrBase
from kernel_w_loop import KernelWLoop

class BenchmarkBase:
    def __init__(self, sm_nr:int, name:str, purpose:str, implicit_replace:bool):
        self.kk_sm = KK_SM(sm_nr, ip='127.0.0.1', port=8180, webload=False)
        self.t_location = os.path.dirname(os.path.realpath(__file__))
        self.sm_nr = self.kk_sm.sass.sm_nr

        # sstr = inspect.getsource(Benchmark)

        self.nogit_prefix = 'nogit__'

        # NOTE: these are mutually exclusive, i.e rd.intersection(wr) == {} and rdwr.intersection(rd) == {}, etc...
        self.rd_data = self.kk_sm.sass.props.measure__data__vared_lat.intersection(self.kk_sm.sass.props.instr_cat__rd)
        self.wr_data = self.kk_sm.sass.props.measure__data__vared_lat.intersection(self.kk_sm.sass.props.instr_cat__wr)
        self.rdwr_data = self.kk_sm.sass.props.measure__data__vared_lat.intersection(self.kk_sm.sass.props.instr_cat__rdwr)
        self.wr_early_data = self.kk_sm.sass.props.measure__data__vared_lat.intersection(self.kk_sm.sass.props.instr_cat__wrearly)

        self.mem_instr_classes = self.kk_sm.sass.props.measure__load_store__vared_lat

        if not os.path.exists('{0}/benchmark_results'.format(self.t_location)):
            os.mkdir('{0}/benchmark_results'.format(self.t_location))

        self.name = name
        self.modified_location = '{0}/benchmark_results/{1}{2}_{3}'.format(self.t_location, self.nogit_prefix, name, sm_nr)
        if implicit_replace and os.path.exists(self.modified_location): shutil.rmtree(self.modified_location)
        os.mkdir(self.modified_location)
        Helpers.create_readme(location=self.modified_location, purpose=purpose, results="")

    @staticmethod
    def create_bin_name_index(bin_index:int, instr_index:int, suffix:str):
        index_name = "{0}.{1}.{2}".format(bin_index, instr_index, suffix)
        if index_name.endswith('.'): index_name = index_name[:-1]
        return index_name
    
    @staticmethod
    def create_target_bin_name(exe_name:str, bin_index:int, instr_index:int, suffix:str):
        file_name = "{0}.{1}".format(exe_name, BenchmarkBase.create_bin_name_index(bin_index, instr_index, suffix))
        return file_name

    @staticmethod
    def target_cubin_to_exe(target_cubin:SM_CuBin_File, exe_name:str, bin_index:int, instr_index:int, suffix:str):
        file_name = BenchmarkBase.create_target_bin_name(exe_name, bin_index, instr_index, suffix)
        target_cubin.to_exec(file_name)
        os.system('chmod +x {0}'.format(file_name))

    @staticmethod
    def create_bins(nr_bins, instrs:typing.List[BInstrBase]) -> typing.List[typing.List[BInstrBase]]:
        total = len(instrs)

        min_bin_size = int(total / nr_bins)
        counts = nr_bins*[min_bin_size]
        remaining = total % min_bin_size
        for r in range(remaining):
            counts[r] += 1
        
        if not (sum(counts) == total): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        instrs_bins = []
        x_from=0
        for s in counts:
            instrs_bins.append(instrs[x_from:(x_from+s)])
            x_from += s
        
        if not ([len(x) for x in instrs_bins] == counts): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        return instrs_bins
    
    @staticmethod
    def normatized_enc_vals_to_str_dict(enc_vals:typing.Dict[str, SASS_Bits]):
        return {ek:str(ev) for ek,ev in enc_vals.items()}

    @staticmethod
    def normatized_instr_component_to_dict(pair:typing.Tuple[str, typing.Dict[str, SASS_Bits]]):
        if not pair: return dict()
        return {'class_name': pair[0], 'enc_vals': BenchmarkBase.normatized_enc_vals_to_str_dict(pair[1])}

    @staticmethod
    def normatized_class_and_enc_vals_to_str(kernel_index:int, class_name:str, enc_vals:typing.Dict[str, SASS_Bits]):
        return "{0}|{1} = {2}".format("Kernel_{0}".format(kernel_index), class_name, BenchmarkBase.normatized_enc_vals_to_str_dict(enc_vals))

    @staticmethod
    def create_modified_binaries_per_k_instructions(kk_sm:KK_SM, nr_bins:int, exe_name_stem:str,
                                 control_props:ControlProps, 
                                 kernel:typing.Type[KernelWLoop], offset:int, instrs:typing.List[BInstrBase],
                                 all_enc_vals_str:typing.List[str]) -> typing.List[str]:
        if not isinstance(kk_sm, KK_SM): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(exe_name_stem, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(nr_bins, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(offset, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(control_props, ControlProps): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instrs, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(all_enc_vals_str, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not (len(all_enc_vals_str) == len(instrs)): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, BInstrBase) for i in instrs): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, str) for i in all_enc_vals_str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not kernel in (KernelWLoop, ): raise Exception

        def create_sub(bin_index:int, kk_sm:KK_SM, exe_name_stem:str,
                       control_props:ControlProps, kernel:typing.Type[KernelWLoop], offset:int,
                       instr_bucket:typing.List[BInstrBase],
                       enc_vals_str_bucket:typing.List[str]):
            nnnnname = BenchmarkBase.create_bin_name_index(bin_index, 0, 'bin')
            print(nnnnname)
            target_cubin = control_props.target_cubin()
            json_list = []
            enc_vals_file = BenchmarkBase.create_target_bin_name(exe_name_stem, bin_index, offset, 'bin') + "_enc_vals.txt"
            enc_vals_json = BenchmarkBase.create_target_bin_name(exe_name_stem, bin_index, offset, 'bin') + "_enc_vals.json"

            
            for instr_index, (bInstr, enc_vals_str) in enumerate(zip(instr_bucket, enc_vals_str_bucket)):    
                output:KernelOutput = kernel.create(kk_sm, control_props, bInstr, kernel_index=instr_index, target_cubin=target_cubin)
                
                # Make sure our enc_vals really match...
                # NOTE: this compares two fairly long strings and can take some time. If something isn't working, using this one is an option
                #       to make sure that we compare apples with apples
                # compare_to = BenchmarkBase.normatized_class_and_enc_vals_to_str(instr_index, bInstr.class_name, bInstr.enc_vals)
                # if not (compare_to == enc_vals_str): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
                if instr_index%100 == 0: print(nnnnname, ":", instr_index, "/", len(instr_bucket))

                # This one allows to exactly reproduce one single benchmark if there is an error.
                json_list.append({
                    'pre_clock_prequels': [BenchmarkBase.normatized_instr_component_to_dict(ii) for ii in bInstr.pre_clock_prequels],
                    'pre_clock_sequels': [BenchmarkBase.normatized_instr_component_to_dict(ii) for ii in bInstr.pre_clock_sequels],
                    'class_name': bInstr.class_name,
                    'enc_vals': BenchmarkBase.normatized_enc_vals_to_str_dict(bInstr.enc_vals),
                    'post_clock_prequels': [BenchmarkBase.normatized_instr_component_to_dict(ii) for ii in bInstr.post_clock_prequels],
                    'post_clock_sequels': [BenchmarkBase.normatized_instr_component_to_dict(ii) for ii in bInstr.post_clock_sequels]
                })
            BenchmarkBase.target_cubin_to_exe(target_cubin, exe_name_stem, bin_index, offset, 'bin')

            with open(enc_vals_json, 'a') as f:
                json.dump(json_list, f, indent=3)
            with open(enc_vals_file, 'w') as f:
                f.write("\n".join(enc_vals_str_bucket))

        nr_kernels = control_props.nr_kernels
        all_bins = [instrs[i:(i+nr_kernels)] for i in range(0, len(instrs), nr_kernels)]
        enc_vals_str_buckets = [all_enc_vals_str[i:(i+nr_kernels)] for i in range(0, len(all_enc_vals_str), nr_kernels)]

        processes = []
        bin_index:int
        instr_bucket:typing.List[BInstrBase]
        all_bin_names = []
        for bin_index,instr_bucket in enumerate(all_bins):
            all_bin_names.append(BenchmarkBase.create_target_bin_name(exe_name_stem, bin_index, offset, 'bin'))

        for bin_index,(instr_bucket, enc_vals_str_bucket) in enumerate(zip(all_bins, enc_vals_str_buckets)):
            # create_sub(bin_index, kk_sm, exe_name_stem, control_props, kernel, instr_bucket, enc_vals_str_bucket)
            p = Process(target=create_sub, args=(bin_index, kk_sm, exe_name_stem, control_props, kernel, offset, instr_bucket, enc_vals_str_bucket))
            processes.append(p)
            p.start()

        p:Process
        for p in processes:
            p.join()

        print("create_modified_binaries with k kernels is finished")
        return all_bin_names

    @staticmethod
    def create_modified_binaries_per_instruction(kk_sm:KK_SM, nr_bins:int, exe_name_stem:str,
                                 control_props:ControlProps, 
                                 kernel:typing.Type[KernelWLoop], instrs:typing.List[BInstrBase]) -> typing.List[str]:
        if not isinstance(kk_sm, KK_SM): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(exe_name_stem, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(nr_bins, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(control_props, ControlProps): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instrs, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not kernel in (KernelWLoop, ): raise Exception

        def create_sub(bin_index:int, kk_sm:KK_SM, exe_name_stem:str,
                       control_props:ControlProps, kernel:typing.Type[KernelWLoop], 
                       instr_bucket:typing.List[BInstrBase]):
            for instr_index, bInstr in enumerate(instr_bucket):
                print(BenchmarkBase.create_bin_name_index(bin_index, instr_index, 'bin'))
                target_cubin = control_props.target_cubin()
                output:KernelOutput = kernel.create(kk_sm, control_props, bInstr, kernel_index=0, target_cubin=target_cubin)
                BenchmarkBase.target_cubin_to_exe(target_cubin, exe_name_stem, bin_index, instr_index, 'bin')

        all_bins = BenchmarkBase.create_bins(nr_bins, instrs)

        processes = []
        bin_index:int
        instr_bucket:typing.List[BInstrBase]
        all_bin_names = []
        for bin_index,instr_bucket in enumerate(all_bins):
            for instr_index, bInstr in enumerate(instr_bucket):
                all_bin_names.append(BenchmarkBase.create_target_bin_name(exe_name_stem, bin_index, instr_index, 'bin'))

        for bin_index,instr_bucket in enumerate(all_bins):
            # create_sub(bin_index, kk_sm, exe_name_stem, control_props, kernel, instr_bucket)
            p = Process(target=create_sub, args=(bin_index, kk_sm, exe_name_stem, control_props, kernel, instr_bucket))
            
            processes.append(p)
            p.start()
            # create_sub(bin_index, kk_sm, exe_name_stem, control_props, kernel, instr_bucket)

        p:Process
        for p in processes:
            p.join()

        print("create_modified_binaries is finished")
        return all_bin_names
