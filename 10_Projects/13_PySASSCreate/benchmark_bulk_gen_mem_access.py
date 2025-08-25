import os
import sys
import re
import typing
import subprocess
import json
import termcolor as tc
from py_sass import SM_SASS
from py_sass import SASS_Class
from py_sass import SASS_Expr
from py_sass import SASS_Class_Props
from py_sass_ext import SASS_Bits
from py_cubin import SM_CuBin_File
from py_sass import TT_List, TT_Param, TT_Reg, TT_Instruction, TT_Func
from py_cubin import Instr_CuBin_Repr, Instr_CuBin_Param_RF, Instr_CuBin_Param_Attr, Instr_CuBin_Param_L
from py_sass import SM_Cu_Props
from py_sass import SM_Cu_Details
from py_sass import SASS_Class, SASS_Class_Props
from py_cubin import SM_CuBin_Regs
from py_cubin import SM_CuBin_File
from py_cubin import SM_CuBin_Utils
from py_cubin import Instr_CuBin
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from sass_create_utils import SASS_Create_Utils
from kk_sm import KK_SM
import _config as sp
from helpers import Helpers
from benchmark_base import BenchmarkBase
from kernel_w_loop_control_props import KernelWLoopControlProps
from kernel_w_loop import KernelWLoop
from binstr_base import BInstrBase
from bulk_generation_utils import GenerationUtils
from bulk_resolve_utils2 import ResolveUtils

class BInstrPrequelResolve(BInstrBase):
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps, main_class_name:str, main_enc_vals:dict):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        # Get the pre-clock prequels by resolving the operands of the current instruction
        pre_clock_prequels, main_enc_vals = ResolveUtils.resolve_operands(kk_sm, main_class_name, main_enc_vals, props)

        # Add the pre-clock prequels
        for class_name, enc_vals in pre_clock_prequels:
            self.add_pre_clock_prequels(class_name, enc_vals)
        # Add the main instruction
        self.add_main(main_class_name, main_enc_vals)
        # No sequels

class Benchmark(BenchmarkBase):
    def __init__(self, sm_nr:int):
        super().__init__(sm_nr, 
                         name='mem',
                         purpose="\n".join(["Benchmark all memory accessing instructions"]),
                        implicit_replace=True)
        
        category = "LD"
        print(tc.colored(category, 'green', attrs=['bold', 'underline']))
        self.kk_sm.sass.load_encdom_small()
        cc_ld = sorted([self.kk_sm.sass.sm.classes_dict[i] for i in self.mem_instr_classes if (self.kk_sm.sass.sm.classes_dict[i].props.opcode.startswith('LD'))], key=lambda x:x.props.opcode)
        pp_ld = ["\n".join([cc.props.opcode, '==========', str(cc.FORMAT), '\n']) for cc in cc_ld]
        # len(pp_ld) == 34
        print(len(cc_ld), "instruction classes to benchmark")
        class_names = [cc.class_name for cc in cc_ld]
        self.create(class_names, "LD")

        category = "ST"
        print(tc.colored(category, 'green', attrs=['bold', 'underline']))
        self.kk_sm.sass.load_encdom_small()
        cc_st = sorted([self.kk_sm.sass.sm.classes_dict[i] for i in self.mem_instr_classes if (self.kk_sm.sass.sm.classes_dict[i].props.opcode.startswith('ST'))], key=lambda x:x.props.opcode)
        pp_st = ["\n".join([cc.props.opcode, '==========', str(cc.FORMAT), '\n']) for cc in cc_st]
        # len(pp_st) = 19
        print(len(cc_st), "instruction classes to benchmark")
        class_names = [cc.class_name for cc in cc_st]
        self.create(class_names, category)

        category = "ATOM"
        print(tc.colored(category, 'green', attrs=['bold', 'underline']))
        self.kk_sm.sass.load_encdom_small()
        cc_atom = sorted([self.kk_sm.sass.sm.classes_dict[i] for i in self.mem_instr_classes if (self.kk_sm.sass.sm.classes_dict[i].props.opcode.startswith('ATOM'))], key=lambda x:x.props.opcode)
        pp_atom = ["\n".join([cc.props.opcode, '==========', str(cc.FORMAT), '\n']) for cc in cc_atom]
        # len(pp_atom) = 33
        print(len(cc_atom), "instruction classes to benchmark")
        class_names = [cc.class_name for cc in cc_atom]
        self.create(class_names, category)

        category = "RED"
        print(tc.colored(category, 'green', attrs=['bold', 'underline']))
        self.kk_sm.sass.load_encdom_small()
        cc_red = sorted([self.kk_sm.sass.sm.classes_dict[i] for i in self.mem_instr_classes if (self.kk_sm.sass.sm.classes_dict[i].props.opcode.startswith('RED'))], key=lambda x:x.props.opcode)
        pp_red = ["\n".join([cc.props.opcode, '==========', str(cc.FORMAT), '\n']) for cc in cc_red]
        # len(pp_red) = 33
        print(len(cc_red), "instruction classes to benchmark")
        class_names = [cc.class_name for cc in cc_red]
        self.create(class_names, category)

        category = "CCTL"
        print(tc.colored(category, 'green', attrs=['bold', 'underline']))
        self.kk_sm.sass.load_encdom_small()
        cc_cctl = sorted([self.kk_sm.sass.sm.classes_dict[i] for i in self.mem_instr_classes if (self.kk_sm.sass.sm.classes_dict[i].props.opcode.startswith('CCTL'))], key=lambda x:x.props.opcode)
        pp_cctl = ["\n".join([cc.props.opcode, '==========', str(cc.FORMAT), '\n']) for cc in cc_cctl]
        # len(pp_cctl) = 11
        print(len(cc_cctl), "instruction classes to benchmark")
        class_names = [cc.class_name for cc in cc_cctl]
        self.create(class_names, category)

        category = "QSPC"
        print(tc.colored(category, 'green', attrs=['bold', 'underline']))
        self.kk_sm.sass.load_encdom_small()
        cc_qspc = sorted([self.kk_sm.sass.sm.classes_dict[i] for i in self.mem_instr_classes if (self.kk_sm.sass.sm.classes_dict[i].props.opcode.startswith('QSPC'))], key=lambda x:x.props.opcode)
        pp_qspc = ["\n".join([cc.props.opcode, '==========', str(cc.FORMAT), '\n']) for cc in cc_qspc]
        # len(pp_qspc) = 15
        print(len(cc_qspc), "instruction classes to benchmark")
        class_names = [cc.class_name for cc in cc_qspc]
        self.create(class_names, category)

        category = "MATCH"
        print(tc.colored(category, 'green', attrs=['bold', 'underline']))
        self.kk_sm.sass.load_encdom_small()
        cc_match = sorted([self.kk_sm.sass.sm.classes_dict[i] for i in self.mem_instr_classes if (self.kk_sm.sass.sm.classes_dict[i].props.opcode.startswith('MATCH'))], key=lambda x:x.props.opcode)
        pp_match = ["\n".join([cc.props.opcode, '==========', str(cc.FORMAT), '\n']) for cc in cc_match]
        # len(pp_match) = 2
        print(len(cc_match), "instruction classes to benchmark")
        class_names = [cc.class_name for cc in cc_match]
        self.create(class_names, category)

        # tot_len = len(pp_ld) + len(pp_st) + len(pp_atom) + len(pp_red) + len(pp_cctl) + len(pp_qspc) + len(pp_match)
        # tot_len == len(self.mem_instr_classes) == 120
        
    
    def create(self, instr_classes:list, category:str):
        # Get all instruction classes that have barriers and no memory access
        TT_Dict = []
        Params = []
        Class_Names = []
        All_Fixed_Params = dict()

        instr_classes_x = sorted(instr_classes)
        instr_classes = instr_classes_x[0:]
        gen_log:dict = dict()
        skipped:list = list()
        class_name:str
        for ind, class_name in enumerate(instr_classes):
            tt_dict, fixed_params, params, size = GenerationUtils.gen_class(self.kk_sm, ind, len(instr_classes), class_name, limit=2**14+1)

            gen_log[class_name] = (len(params), size)
            # There may be instructions that yield a way to large amount of variants if we include everything...
            if len(params) == 0 and size > 0:
                skipped.append({'class_name': class_name, 'size': size})
            else:
                Params.extend(params)
                TT_Dict.extend(len(params)*[tt_dict])
                Class_Names.extend(len(params)*[class_name])
                All_Fixed_Params[class_name] = list(fixed_params)
        
        for c,v in sorted(gen_log.items(), key=lambda x:x[1][0], reverse=True): print(c,"valid: {0}/{1}".format(v[0],v[1]))
        print("===========")
        with open("{0}/{1}".format(self.modified_location, "skipped_because_too_large.json"), 'w') as f:
            json.dump(skipped, f)
        with open("{0}/{1}".format(self.modified_location, "fixed_params.json"), 'w') as f:
            json.dump(All_Fixed_Params, f)

        print("Process yielded")
        print("   [{0}] total number of feasible instructions with [{1}] number of variants".format(len(Class_Names), len(Params)))
        print("   [{0}] total number of infeasible instructions".format(len(skipped)))

        # print("Total:", sum(dddd.values()))
        # return

        # template = "{0}/{1}".format(self.t_location, "template_3000i/benchmark_binaries/template_3000i_{0}".format(self.sm_nr))
        print("Load kernel template...")
        template = "{0}/{1}".format(self.t_location, "template_projects/template_1000k/benchmark_binaries/template_1000k_{0}".format(self.sm_nr))
        props = KernelWLoop.get_kernel_control_props(
            self.kk_sm, 
            empty_instr=False, 
            loop_count=10, 
            template=template,
            increment_output=True,
            increment_input_as_well=False)

        all_enc_vals_str = []
        instr = []
        
        for kernel_index,(class_name, enc_vals) in enumerate(zip(Class_Names, Params)):
            # if class_name != 'ldc_ur__URRzI': continue
            if (kernel_index%100 == 0) or (kernel_index == len(Params)-1): print("[{0}/{1}] Create kernels...".format(kernel_index, len(Class_Names)-1), end='')
            ii = BInstrPrequelResolve(self.kk_sm, props, class_name, enc_vals)
            all_enc_vals_str.append(BenchmarkBase.normatized_class_and_enc_vals_to_str(kernel_index%props.nr_kernels, ii.class_name, ii.enc_vals))
            instr.append(ii)
            if (kernel_index%100 == 0) or (kernel_index == len(Params)-1): print("Ok")

        # Need to delete this one because of the multiprocessing module...
        self.kk_sm.sass.remove_loaded_encdom()
        
        print("Finished...Generate cubins...", flush=True)
        generated_bins = []
        # Stick to 4x1000 for memory reasons
        exe_name_stem = '{0}/{1}_{2}'.format(self.modified_location, self.name, category)
        max_range = 4000
        for offset in range(0, len(instr), max_range):
            print("...Range [{0} - {1}/{2}]...".format(offset, offset + max_range, len(instr)))
            generated_bins_x = BenchmarkBase.create_modified_binaries_per_k_instructions(self.kk_sm, 2, exe_name_stem, props, KernelWLoop, offset, instr[offset:(offset+max_range)], all_enc_vals_str[offset:(offset+max_range)])
            generated_bins.extend(generated_bins_x)
        print("Finished...Running all generated cubins...", flush=True)
        
        results = Helpers.run_bin_loop(1, 2, generated_bins, True)
        with open("{0}/log.ansi".format(self.modified_location), 'w') as f:
            Helpers.process_output_multi_kernel_w_loop_results(results, 5000, file_obj=f)

        some_code = """import json
import os
import json

with open("{0}/fixed_params.json".format(os.path.dirname(os.path.realpath(__file__))), 'r') as f:
   jj = json.load(f)

[print("'{0}',".format(i), end='') for i in jj.keys()]
[print(i) for i in jj.keys()]

"""
        with open("{0}/generated_bins.py".format(self.modified_location), 'w') as f:
            f.write(some_code)
            f.write("generated_bins = [\n{0}\n]".format("   '" + "',\n   '".join(generated_bins) + "'"))
        print("[Finished {0}]".format(category))

if __name__ == '__main__':
    shortcut = False

    if shortcut:
        generated_bins = []
        result_log_path = "/".join(generated_bins[0].split('/')[:-1]) + '/log.ansi'
        results = Helpers.run_bin_loop(1, 15, generated_bins, True)
        with open(result_log_path, 'w') as f:
            Helpers.process_output_multi_kernel_w_loop_results(results, 5000, file_obj=f)

        pass
    else:
        # Generator
        Benchmark(86)
