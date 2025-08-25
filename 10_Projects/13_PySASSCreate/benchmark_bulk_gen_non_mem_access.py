import os
import sys
import re
import typing
import subprocess
import json
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
from bulk_resolve_utils import ResolveUtils

class BInstrPrequelResolve(BInstrBase):
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps, main_class_name:str, main_enc_vals:dict):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        # Get the pre-clock prequels by resolving the operands of the current instruction
        pre_clock_prequels = ResolveUtils.resolve_operands(kk_sm, main_class_name, main_enc_vals, props)

        # Add the pre-clock prequels
        for class_name, enc_vals in pre_clock_prequels:
            self.add_pre_clock_prequels(class_name, enc_vals)
        # Add the main instruction
        self.add_main(main_class_name, main_enc_vals)
        # No sequels

class Benchmark(BenchmarkBase):
    def __init__(self, sm_nr:int):
        super().__init__(sm_nr, 
                         name='non_mem',
                         purpose="\n".join(["Benchmark all non-memory accessing instructions"]),
                        implicit_replace=True)

        self.kk_sm.sass.load_encdom_small()

        # Get all instruction classes that have barriers and no memory access
        TT_Dict = []
        Params = []
        Class_Names = []
        All_Fixed_Params = dict()
        all_data_classes = self.rd_data.union(self.wr_data).union(self.rdwr_data).union(self.wr_early_data)

        finished_classes = {
            "dmul__RCR_RC","dadd__RRC_RC","dfma__RsIR_RIR","dfma__RUR_RUR","dfma__RCR_RCR","dmul__RCxR_RCx","dfma__RCxR_RCxR","dfma__RRCx_RRCx","dmul__RsIR_RI","dfma__RRsI_RRI","dmul__RRR_RR","dadd__RRU_RU","dmul__RUR_RU","dadd__RRsI_RI","dfma__RRU_RRU","dadd__RRR_RR","dadd__RRCx_RCx","dfma__RRC_RRC","dfma__RRR_RRR",
            'i2f_Rd64__Rb_8b','i2f_Rd64__IS_64b','i2f_Rd64__Rb_16b','i2f__CX_64b','i2f_Rd64__CX_32b','i2f_Rd64__UR_8b','i2f__UR_8b','i2f__UR_64b','i2f__IS_32b','i2f_Rd64__Rb_32b','i2f_Rd64__Rb_64b','i2f__Rb_64b','i2f__Rb_8b','i2f__Cb_16b','i2f_Rd64__CX_8b','i2f__Rb_32b','i2f__Cb_8b','i2f_Rd64__IU_32b','i2f_Rd64__Cb_32b','i2f_Rd64__IU_64b','i2f_Rd64__UR_64b','i2f_Rd64__UR_32b','i2f__Cb_64b','i2f_Rd64__Cb_64b','i2f__Rb_16b','i2f__CX_32b','i2f_Rd64__IS_32b','i2f__IS_64b','i2f_Rd64__Cb_8b','i2f__CX_8b','i2f_Rd64__CX_64b','i2f__CX_16b','i2f_Rd64__CX_16b','i2f__UR_32b','i2f_Rd64__Cb_16b','i2f__UR_16b','i2f_Rd64__UR_16b','i2f__IU_64b','i2f__Cb_32b','i2f__IU_32b',
            'f2f_f64_downconvert__RUR_RUR','f2f_f64_upconvert__R_CX32_R_RCXR','f2f_f64_upconvert__R_I16_R_RIR','f2f_f32_upconvert__RUR_RUR','f2f_f64_downconvert__RIR_RIR','f2f_f64_upconvert__R_R16_R_RRR','f2f_f64_upconvert__R_C16_R_RCR','f2f_f64_upconvert__R_CX16_R_RCXR','f2f_f64_upconvert__R_32I_R_RIR','f2f_f32_upconvert__RCR_RCR','f2f_f32_downconvert__RIR_RIR','f2f_f64_upconvert__R_UR32_R_RUR','f2f_f64_downconvert__RCXR_RCXR','f2f_f32_upconvert__RCXR_RCXR','f2f_f64_downconvert__RRR_RRR','f2f_f32_downconvert__RUR_RUR','f2f_f64_upconvert__R_C32_R_RCR','f2f_f32_downconvert__RRR_RRR','f2f_f64_downconvert__RCR_RCR','f2f_f64_upconvert__R_R32_R_RRR','f2f_f32_downconvert__RCR_RCR','f2f_f64_upconvert__R_UR16_R_RUR','f2f_f32_downconvert__RCXR_RCXR','f2f_f32_upconvert__RIR_RIR','f2f_f32_upconvert__RRR_RRR',
            'f2i_Rd64__Rb_16b','f2i__Ib_16b','f2i__CXb_64b','f2i__Ib_64b','f2i__URb_64b','f2i__Rb_16b','f2i_Rd64__URb_16b','f2i_Rd64__Ib_64b','f2i_Rd64__CXb_16b','f2i_Rd64__Ib_16b','f2i__Cb_32b','f2i_Rd64__CXb_32b','f2i__IU_32b','f2i__CXb_32b','f2i_Rd64__IU_32b','f2i_Rd64__Cb_32b','f2i_Rd64__Rb_32b','f2i_Rd64__CXb_64b','f2i_Rd64__URb_64b','f2i_Rd64__Rb_64b','f2i__CXb_16b','f2i_Rd64__URb_32b','f2i__Rb_32b','f2i__URb_16b','f2i_Rd64__Cb_64b','f2i__Rb_64b','f2i_Rd64__Cb_16b','f2i__Cb_64b','f2i__Cb_16b','f2i__URb_32b',
            'fchk__RUR_RU','brev__RCxR_RCxR','fchk__RIR_RI','clmad__RUR_RUR','clmad__RRC_RRC','fchk__RCxR_RCx','dsetp__RRCx_RCx','footprint_scr_b_','frnd__f16_URb','frnd__f16_C','frnd__f64_C','fchk__RRR_RR','footprint_scr_','footprint_scr_uniform_','frnd__f32_I','flo__RCR_RCR','clmad__RRR_RRR','brev__RCR_RCR','dsetp_simple__RRR_RR','brev__RUR_RUR','brev__RRR_RRR','frnd__f64_URb','brev__RuIR_RIR','frnd__f64_R','clmad__RRCx_RRCx','flo__RRR_RRR','flo__RUR_RUR','frnd__f64_I','frnd__f32_C','dsetp_simple__RRC_RC','footprint_b_','footprint_scr_b_tid_','dsetp_simple__RRU_RU','dsetp_simple__RRCx_RCx','frnd__f32_R','frnd__f16_I','dsetp__RRU_RU','flo__RCxR_RCxR','flo__RuIR_RIR','footprint_uniform_','footprint_b_noConst_','footprint_b_tid_','clmad__RCR_RCR','clmad__RCxR_RCxR','frnd__f16_R','frnd__f32_URb','dsetp__RRsI_RI','dsetp__RRC_RC','footprint_','dsetp__RRR_RR','frnd__f64_CXb','footprint_scr_b_noConst_','frnd__f32_CXb','frnd__f16_CXb','clmad__RRU_RRU','dsetp_simple__RRsI_RI','fchk__RCR_RC',
            'tmml_b_tid_','mufu__RIR_RI','hmma_sparse_','shfl__RRR','hmma_x8_','mufu_fp16__RC','popc__RRR_RRR','imma_','popc__RuIR_RIR','mufu__RUR_RU','bmma_','hmma_x8_indexedRF_','popc__RUR_RUR','tmml_urc_','mufu__RCR_RC','popc__RCxR_RCxR','mufu_fp16__RI','mufu__RCxR_RCx','hmma_sparse_indexedRF_','mufu__RRR_RR','tmml_b_noConst_','shfl__RII','tmml_','shfl__RIR','popc__RCR_RCR','mufu_fp16__RCx','mufu_fp16__RR','tmml_b_','mufu_fp16__RU','shfl__RRI',
            'txd_urc_','txq_','txd_b_tid_','tex_b_tid_','txq_b_tid_','tex_scr_urc_','txd_','tex_','txd_b_','txq_urc_','txq_b_noConst_','txd_b_noConst_','tex_urc_','tex_scr_','tex_scr_b_','txq_b_','tex_b_noConst_','tex_b_','tex_scr_b_tid_','tex_scr_b_noConst_',
            'tld4_scr_b_','tld_b_noConst_','tld4_scr_urc_','tld_urc_','tld_scr_b_','tld4_scr_b_noConst_','tld4_scr_','tld4_b_tid_','tld_b_','tld_scr_urc_','tld4_urc_','tld_scr_b_noConst_','tld_','tld_b_tid_','tld4_','tld4_b_','tld_scr_','tld_scr_b_tid_','tld4_scr_b_tid_','tld4_b_noConst_',
            'dmma_','ldtram_','ast__LOGICAL_RaRZ','suquery_tid_','pixld_','arrives_','ald__PATCH_RaNonRZOffset_P_RbRZ','r2b_','s2ur_','ast__PATCH_RaRZ','movm_','suquery_urc_','ald_UR__PATCH_URa_P_RbRZ','s2r_','ttuld__no_close','ald_PHYS_','isberd_','r2ur__OR','out__CUT','setctaid_','ast__PATCH_RaNonRZOffset','ald_UR__LOGICAL_URa_default','suquery_reg_','ttuld__close','suquery_imm_','getlmembase_','ast_UR__LOGICAL_URa','ast_UR__PATCH_RaRZ_URa','out__EMIT_Imm','r2ur__noOR','al2p__RaNonRZ','setlmembase_','ast_PHYS_','isbewr_','ald__PATCH_RaRZ_P_RbRZ','al2p__RaRZ','redux_','out__EMIT_URb','ald__LOGICAL_RaRZ_default','ttust_','out__EMIT_Rb','ttuclose_','out__FINAL',
            'ipa_offset__IPA_Ib','ipa_ur_offset__IPA_URa_Ib','ipa_ur_','ipa_','ipa_offset__IPA_C','ipa_ur_offset__IPA_URa_Rb','ipa_offset__IPA_Rb',
            'imma_sp_',
            "sust_p_reg_","sust_p_urc_","suld_p_reg_","suld_d_reg_","sust_p_imm_","sust_d_tid_","suld_p_urc_","sust_p_tid_","suld_p_tid_","sust_d_urc_","sust_d_reg_","suld_d_urc_","suld_p_imm_","suld_d_tid_","suld_d_imm_","sust_d_imm_","suatom_cas_imm_","suatom_cas_urc_","suatom_cas_reg_","suatom_cas_tid_",
            'sured_urc_','sured_imm_','sured_tid_','sured_reg_'}
        all_data_classes = all_data_classes.difference(finished_classes)

        dddd = dict()
        skipped = []

        # Remaining ones: not really relevant for the regular Cuda program
        # "suatom_urc_", 6291456
        # "suatom_reg_", 6291456
        # "suatom_tid_", 6291456
        # "suatom_imm_", 6291456
        
        
        class_name:str
        for ind, class_name in enumerate(all_data_classes):
            if not class_name in ["sured_imm_", "sured_reg_", "sured_tid_", "sured_urc_"]: continue
            # if not ('i2f' in class_name.lower()): continue
            # if not class_name in ["sust_p_reg_","sust_p_urc_","suld_p_reg_","suld_d_reg_","sust_p_imm_","sust_d_tid_","suld_p_urc_","sust_p_tid_","suld_p_tid_","sust_d_urc_","sust_d_reg_","suld_d_urc_","suld_p_imm_","suld_d_tid_","suld_d_imm_","sust_d_imm_","suatom_cas_imm_","suatom_cas_urc_","suatom_cas_reg_","suatom_cas_tid_"]: continue
            # if not any(class_name.find(j)>=0 for j in ['txq', 'txd', 'tex']): continue
            # if ('dfma' not in class_name) and ('dmul' not in class_name) and ('dadd' not in class_name): continue
            # if class_name != 'imma_sp_': continue
            # if class_name != 'dfma__RRC_RRC': continue
            # if class_name != 'dfma__RCxR_RCxR': continue
            # if class_name != 'dadd__RRC_RC': continue
            # if class_name != 'sured_tid_': continue
            # if class_name != 'shfl__RRR': continue
            # if class_name != 'ald_UR__PATCH_URa_P_RbRZ': continue
            # if class_name != 'setctaid_': continue
            # if class_name != 'arrives_': continue

            tt_dict, fixed_params, params, size = GenerationUtils.gen_class(self.kk_sm, ind, len(all_data_classes), class_name, limit=2**14+1)

            dddd[class_name] = (len(params), size)
            # There may be instructions that yield a way to large amount of variants if we include everything...
            if len(params) == 0 and size > 0:
                skipped.append({'class_name': class_name, 'size': size})
            else:
                Params.extend(params)
                TT_Dict.extend(len(params)*[tt_dict])
                Class_Names.extend(len(params)*[class_name])
                All_Fixed_Params[class_name] = list(fixed_params)
        
        for c,v in sorted(dddd.items(), key=lambda x:x[1][0], reverse=True): print(c,"valid: {0}/{1}".format(v[0],v[1]))
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
        props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)

        all_enc_vals_str = []
        instr = []
        for kernel_index,(class_name, enc_vals) in enumerate(zip(Class_Names, Params)):
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
        exe_name_stem = '{0}/{1}'.format(self.modified_location, self.name)
        max_range = 2000
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
        print("[Finished]")

if __name__ == '__main__':
    shortcut = False

    if shortcut:
        generated_bins = [
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.0.0.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.1.0.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.2.0.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.3.0.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.0.4000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.1.4000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.2.4000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.3.4000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.0.8000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.1.8000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.2.8000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.3.8000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.0.12000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.1.12000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.2.12000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.3.12000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.0.16000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.1.16000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.2.16000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.3.16000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.0.20000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.1.20000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.2.20000.bin',
        '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/keep__non_mem_86.5/non_mem.3.20000.bin'
        ]
        result_log_path = "/".join(generated_bins[0].split('/')[:-1]) + '/log.ansi'
        results = Helpers.run_bin_loop(1, 15, generated_bins, True)
        with open(result_log_path, 'w') as f:
            Helpers.process_output_multi_kernel_w_loop_results(results, 5000, file_obj=f)

        pass
    else:
        # Generator
        Benchmark(86)
