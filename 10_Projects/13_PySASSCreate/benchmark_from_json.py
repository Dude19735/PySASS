import sys
import os
import typing
import datetime
import shutil
import termcolor as tc
import json
from multiprocessing import Process
from py_cubin import SM_CuBin_File, SM_CuBin_Utils
from py_sass import SASS_Class
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
import _config as sp
from helpers import Helpers
from kernel_output import KernelOutput
from kernel_w_loop_control_props import KernelWLoopControlProps
from binstr_base import BInstrBase
from kernel_w_loop import KernelWLoop
from benchmark_base import BenchmarkBase
import sass_create as sc

class BInstr(BInstrBase):
    """This one gets it's instructions from a dictionary
    """
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps, enc_vals_dict:dict):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        # Add all the stuff we loaded from the dictionary
        BInstr.add(self.add_pre_clock_prequels, enc_vals_dict['pre_clock_prequels'])
        BInstr.add(self.add_post_clock_prequels, enc_vals_dict['post_clock_prequels'])
        BInstr.add(self.add_main, [enc_vals_dict])
        BInstr.add(self.add_pre_clock_sequels, enc_vals_dict['pre_clock_sequels'])
        BInstr.add(self.add_post_clock_sequels, enc_vals_dict['post_clock_sequels'])

    @staticmethod
    def add(func:typing.Callable, source:list):
        for pp in source:
            func(pp['class_name'], {k: SM_CuBin_Utils.sass_bits_from_str(str(v)) for k,v in pp['enc_vals'].items()})

        
class Benchmark(BenchmarkBase):
    def __init__(self, sm_nr:int, enc_vals_dict:dict, single_kernel:bool=True):
        super().__init__(sm_nr, 
                         name='json_b',
                         purpose="\n".join([
                            "This one creates a kernel corresponding to the entries in a json file that is produced my the mass-testing approach.",
                            "",
                            "It serves to debug stuff that doesn't produce the desired result."]),
                        implicit_replace=True)

        print(tc.colored("Experiment 1", 'green', attrs=['bold', 'underline']))
        # Experiment 1: use usched_info = wait
        ######################################
        if single_kernel:
            template = '{0}/template_projects/template_1k/benchmark_binaries/template_1k_{1}.bin'.format(self.t_location, self.sm_nr)
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            
            # Custom changes for debugging
            # ============================
            # enc_vals_dict['pre_clock_prequels'][-1]['enc_vals']['']

            bInstr = BInstr(self.kk_sm, props, enc_vals_dict)
            exe_name_stem = '{0}/{1}'.format(self.modified_location, 'bin_file')
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, [bInstr])
            results = Helpers.run_single_kernel_bin(exe_name=generated_bins[0], exe_arg=str(props.loop_count))
            print()
            print("Test results with barrier and wait")
            Helpers.output_print_single_kernel_w_loop_results(results, 0, props, output=Helpers.CONST__DOutput)
        else:
            template = '{0}/template_projects/template_1k_loop/benchmark_binaries/template_1k_loop_{1}.bin'.format(self.t_location, self.sm_nr)
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)

            bInstr = BInstr(self.kk_sm, props, enc_vals_dict)
            all_enc_vals_str = [BenchmarkBase.normatized_class_and_enc_vals_to_str(0, bInstr.class_name, bInstr.enc_vals)]
            exe_name_stem = '{0}/{1}'.format(self.modified_location, 'bin_file')
            generated_bins = BenchmarkBase.create_modified_binaries_per_k_instructions(self.kk_sm, 4, exe_name_stem, props, KernelWLoop, 0, [bInstr], all_enc_vals_str)
            
            results = Helpers.run_bin_loop(1, props.loop_count, generated_bins, True)
            Helpers.process_output_multi_kernel_w_loop_results(results, 5000)

if __name__ == '__main__':
    t_location = os.path.dirname(os.path.realpath(__file__))
    experiment1 = "{0}/{1}".format(t_location, 'benchmark_results/nogit__non_mem_86/non_mem.0.0.bin_enc_vals.json')
    # # footprint_scr_, 766
    # experiment2 = "{0}/{1}".format(t_location, 'benchmark_results/nogit__non_mem_86/non_mem.0.4000.bin_enc_vals.json')
    # # footprint_uniform_, 0
    # # footprint_b_noConst_, 114
    # # footprint_b_tid_, 168
    # experiment3 = "{0}/{1}".format(t_location, 'benchmark_results/nogit__non_mem_86/non_mem.2.8000.bin_enc_vals.json')
    # # footprint_, 212
    # experiment4 = "{0}/{1}".format(t_location, 'benchmark_results/nogit__non_mem_86/non_mem.1.16000.bin_enc_vals.json')
    # # footprint_scr_b_noConst_, 438
    # experiment5 = "{0}/{1}".format(t_location, 'benchmark_results/nogit__non_mem_86/non_mem.3.20000.bin_enc_vals.json')

    experiment = experiment1
    index = 8
    
    with open(experiment, 'r') as f:
        jj = json.load(f)
    b = Benchmark(86, jj[index], single_kernel=False)
    print("Finished")
    pass
