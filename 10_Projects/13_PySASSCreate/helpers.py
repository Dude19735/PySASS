from __future__ import annotations
import re
import sys
import os
import subprocess
import typing
import json
import termcolor as tc
import _config as sp
from py_sass_ext import SASS_Bits
from py_cubin import Instr_CuBin_Repr, SM_CuBin_File
from kernel_output import KernelOutput
from kernel_w_loop_control_props import KernelWLoopControlProps

class Helpers:
    # All kernel types
    CONST__Filename = 'Filename'
    CONST__Input = 'Input'

    CONST__Control = 'Control'
    CONST__UiOutput = 'UiOutput'
    CONST__DOutput = 'DOutput'
    CONST__FOutput = 'FOutput'
    CONST__UiInput = 'UiInput'
    CONST__DInput = 'DInput'
    CONST__ClkOut1 = 'ClkOut1'
    CONST__UiInput0 = 'UiInput0'
    CONST__DInput0 = 'DInput0'
    CONST__BeforeKernel = 'BeforeKernel'
    CONST__CUDAError = 'CUDAError'
    CONST__AfterKernel = 'AfterKernel'

    # Multikernel only
    CONST__EncValsFile = 'EncValsFile'
    CONST__EncVals = 'EncVals'
    CONST__KernelCount = 'KernelCount'
    CONST__UsedKernelCount = 'UsedKernelCount'
    CONST__Results = 'Results'
    CONST__KernelAddress = 'KernelAddress'

    @staticmethod
    def create_readme(location:str, purpose:str, results:str):
        with open("{0}/readme.md".format(location), 'w') as f:
            f.write("### Purpose\n{0}\n\n### Results\n{1}\n".format(purpose, results))

    @staticmethod
    def snip_str(msg:str, key:str) -> str:
        start = [m.end() for m in re.finditer(r'\[{0}\]'.format(key), msg)]
        end = [m.start() for m in re.finditer(r'\[/{0}\]'.format(key), msg)]
        
        if len(start) == 0 and len(end) == 0: return ""
        if key == Helpers.CONST__CUDAError:
            return "<" + "><".join(["[{0}]: {1}".format(ind, msg[s:e]) for ind,(s,e) in enumerate(zip(start, end))]) + ">"
        else:
            if not len(start)<=1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if not len(end)<=1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            return msg[start[0]:end[0]]

    @staticmethod
    def parse_bf(output:str) -> dict:
        control = Helpers.snip_str(output, Helpers.CONST__Control)
        ui_output = Helpers.snip_str(output, Helpers.CONST__UiOutput)
        d_output = Helpers.snip_str(output, Helpers.CONST__DOutput)
        f_output = Helpers.snip_str(output, Helpers.CONST__FOutput)
        ui_input = Helpers.snip_str(output, Helpers.CONST__UiInput)
        d_input = Helpers.snip_str(output, Helpers.CONST__DInput)
        clk_out_1 = Helpers.snip_str(output, Helpers.CONST__ClkOut1)
        ui_input0 = Helpers.snip_str(output, Helpers.CONST__UiInput0)
        d_input0 = Helpers.snip_str(output, Helpers.CONST__DInput0)

        return {
            Helpers.CONST__Control: [int(i.strip()) for i in control.split(',')],
            Helpers.CONST__UiOutput: [int(i.strip()) for i in ui_output.split(',')],
            Helpers.CONST__DOutput: [float(i.strip()) for i in d_output.split(',')],
            Helpers.CONST__FOutput: [float(i.strip()) for i in f_output.split(',')],
            Helpers.CONST__UiInput: [int(i.strip()) for i in ui_input.split(',')],
            Helpers.CONST__DInput: [float(i.strip()) for i in d_input.split(',')],
            Helpers.CONST__ClkOut1: [int(i.strip()) for i in clk_out_1.split(',')]
        }

    @staticmethod
    def parse_err(err:str) -> dict:
        return err

    @staticmethod
    def parse_single_kernel_loop(loop:str) -> dict:
        before = Helpers.parse_bf(Helpers.snip_str(loop, Helpers.CONST__BeforeKernel))
        err = Helpers.parse_err(Helpers.snip_str(loop, Helpers.CONST__CUDAError))
        after = Helpers.parse_bf(Helpers.snip_str(loop, Helpers.CONST__AfterKernel))

        return {Helpers.CONST__BeforeKernel: before, Helpers.CONST__CUDAError: err, Helpers.CONST__AfterKernel: after}

    @staticmethod
    def parse_single_kernel_results(msg:str) -> typing.List[dict]:
        if(msg[:50].find(Helpers.CONST__EncVals) >= 0): raise Exception(sp.CONST__ERROR_ILLEGAL)

        all_loop_starts = [m.end() for m in re.finditer(r'\[LoopCount_([0-9]+)\]', msg)]
        all_loop_ends = [m.start() for m in re.finditer(r'\[/LoopCount_([0-9]+)\]', msg)]
        all_loops = [Helpers.parse_single_kernel_loop(msg[s:e]) for s,e in zip(all_loop_starts, all_loop_ends)]
        return all_loops
    
    @staticmethod
    def parse_multi_kernel_loop(msg:str) -> typing.Dict:
        enc_vals = Helpers.snip_str(msg, Helpers.CONST__EncVals).strip()
        kernel_address = Helpers.snip_str(msg, Helpers.CONST__KernelAddress).strip()
        ff = "[/{0}]".format(Helpers.CONST__EncVals)
        enc_vals_end_ind = msg.find(ff) + len(ff) + 1
        loop_results = Helpers.parse_single_kernel_results(msg[enc_vals_end_ind:])
        
        return {
            Helpers.CONST__EncVals: enc_vals,
            Helpers.CONST__KernelAddress: kernel_address,
            Helpers.CONST__Results: loop_results
        }
    
    @staticmethod
    def check_multi_kernel_results(mk_results:dict):
        enc_vals_file = mk_results[Helpers.CONST__EncValsFile]
        all_enc_vals = [i[Helpers.CONST__EncVals] for i in  mk_results[Helpers.CONST__Results]]
        
        with open(enc_vals_file, 'r') as f:
            enc_vals_comp = f.read()

        enc_vals_comp = enc_vals_comp.split('\n')
        
        for ind, (av,ec) in enumerate(zip(all_enc_vals, enc_vals_comp)):
            if not (av == ec):
                err_msg = "EncVals for Kernel_{0} in results don't match:\n   Expected: {1}\n   Received: {2}\n".format(ind, av, ec)
                raise Exception(err_msg)
    
    @staticmethod
    def parse_multi_kernel_result(msg:str) -> typing.List[dict]:
        filename = Helpers.snip_str(msg, Helpers.CONST__Filename)
        input_nr = Helpers.snip_str(msg, Helpers.CONST__Input)
        enc_vals_file = Helpers.snip_str(msg, Helpers.CONST__EncValsFile)
        kernel_count = Helpers.snip_str(msg, Helpers.CONST__KernelCount)
        used_kernel_count = Helpers.snip_str(msg, Helpers.CONST__UsedKernelCount)

        k_count = int(kernel_count)
        used_k_count = int(used_kernel_count)
        all_k_starts = [m.end() for m in re.finditer(r'\[Kernel_([0-9]+)\]', msg)]
        all_k_ends = [m.start() for m in re.finditer(r'\[/Kernel_([0-9]+)\]', msg)]

        if not ((len(all_k_starts) == used_k_count) and (len(all_k_ends) == used_k_count)): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        all_ks = [Helpers.parse_multi_kernel_loop(msg[s:e]) for s,e in zip(all_k_starts, all_k_ends)]

        results = {
            Helpers.CONST__Filename: filename,
            Helpers.CONST__Input: int(input_nr),
            Helpers.CONST__EncValsFile: enc_vals_file,
            Helpers.CONST__KernelCount: k_count,
            Helpers.CONST__UsedKernelCount: int(used_kernel_count),
            Helpers.CONST__Results: all_ks
        }

        Helpers.check_multi_kernel_results(results)
        return results
    
    @staticmethod
    def run_single_kernel_bin(exe_name:str, exe_arg:str):
        result = subprocess.run(['{0}'.format(exe_name), exe_arg], capture_output=True, text=True)
        parsed_result = Helpers.parse_single_kernel_results(result.stdout)
        return parsed_result
    
    @staticmethod
    def run_multi_kernel_bin(exe_name:str, exe_arg:str) -> typing.List[dict]:
        result = subprocess.run(['{0}'.format(exe_name), exe_arg, "/".join(exe_name.split('/')[:-1])], capture_output=True, text=True)
        parsed_result = Helpers.parse_multi_kernel_result(result.stdout)
        return parsed_result

    @staticmethod
    def run_bin_loop(outer_loop_count:int, inner_loop_count:int, all_bin_names:list, multi_kernel:bool) -> typing.List[typing.List[typing.Dict]]:
        if not isinstance(outer_loop_count, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(inner_loop_count, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(all_bin_names, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(multi_kernel, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)

        outer_loops = [[] for i in range(len(all_bin_names))]
        if multi_kernel:
            for e in range(outer_loop_count):
                for ind, bin in enumerate(all_bin_names):
                    print("[{0}/{1}] Running {2}...".format(ind+1, len(all_bin_names), bin), end='', flush=True)
                    results = Helpers.run_multi_kernel_bin(exe_name=bin, exe_arg=str(inner_loop_count))
                    print("Ok", flush=True)
                    outer_loops[ind].append(results)
        else:
            for e in range(outer_loop_count):
                for ind, bin in enumerate(all_bin_names):
                    print("[{0}/{1}] Running {2}...".format(ind+1, len(all_bin_names), bin), end='', flush=True)
                    results = Helpers.run_single_kernel_bin(exe_name=bin, exe_arg=str(inner_loop_count))
                    print("Ok", flush=True)
                    outer_loops[ind].append(results)
    
        return outer_loops
    
    @staticmethod
    def get_con_ok(condition:bool):
        if condition: return tc.colored("OK", 'green')
        return tc.colored("ERROR", 'red', attrs=['bold'])

    @staticmethod
    def output_print_single_kernel_w_loop_results(results:dict, expected_result:int|float|list, props:KernelWLoopControlProps, output:str, output_all_arrays=False):
        if not output in (Helpers.CONST__UiOutput, Helpers.CONST__DOutput, Helpers.CONST__FOutput):
            raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        actual_loop_count:int = results[0][Helpers.CONST__AfterKernel][Helpers.CONST__Control][1]
        actual_exec_loop_count:int = results[0][Helpers.CONST__AfterKernel][Helpers.CONST__Control][2]
        actual_result:int = results[0][Helpers.CONST__AfterKernel][Helpers.CONST__Control][0]
        all_results:list = results[0][Helpers.CONST__AfterKernel][output]
        actual_kernel_index:int = results[0][Helpers.CONST__AfterKernel][Helpers.CONST__Control][4]
        shader_stage_index:int = results[0][Helpers.CONST__AfterKernel][Helpers.CONST__Control][5]

        def output_arrays(const_str:str):
            print(const_str)
            print("   ", Helpers.CONST__BeforeKernel, ":", results[0][Helpers.CONST__BeforeKernel][const_str])
            print("   ", Helpers.CONST__AfterKernel, ": ", results[0][Helpers.CONST__AfterKernel][const_str])

        if output_all_arrays:
            output_arrays(Helpers.CONST__UiInput)
            output_arrays(Helpers.CONST__DInput)
            output_arrays(Helpers.CONST__UiOutput)
            output_arrays(Helpers.CONST__DOutput)
            output_arrays(Helpers.CONST__FOutput)

        print("This one should be empty: CudaErr: ", tc.colored(results[0][Helpers.CONST__CUDAError], 'red', attrs=['bold']))
        print("This one should be 815: ", actual_result, "[{0}]".format(Helpers.get_con_ok(actual_result == 815)))
        print("This one must match the required loop_count {0}: ".format(props.loop_count), actual_loop_count, "[{0}]".format(Helpers.get_con_ok(actual_loop_count == props.loop_count)))
        print("This is the executed loop_count {0}: ".format(props.loop_count), actual_exec_loop_count, "[{0}]".format(Helpers.get_con_ok(actual_exec_loop_count == props.loop_count)))
        print("This is the the cycle count of the last iteration: ", results[0][Helpers.CONST__AfterKernel][Helpers.CONST__Control][3])
        print("This is the kernel index and should be 0: ", actual_kernel_index, "[{0}]".format(Helpers.get_con_ok(actual_kernel_index==0)))
        print("This is the shader stage index and should be 0: ", shader_stage_index, "[{0}]".format(Helpers.get_con_ok(shader_stage_index==0)))
        if isinstance(expected_result, int|float):
            if props.increment_output:
                print("This ones should all be {0}: ".format(expected_result), all_results, "[{0}]".format(Helpers.get_con_ok(all(res==expected_result for res in all_results))))
            else:
                print("This ones first entry should be {0}: ".format(expected_result), all_results, "[{0}]".format(Helpers.get_con_ok(all_results[0]==expected_result)))
        elif isinstance(expected_result, list):
            if props.increment_output:
                print("This ones entries should match with {0}: ".format(expected_result))
                print("                                    {0}: ".format(all_results), "[{0}]".format(Helpers.get_con_ok(expected_result==all_results)))
            else:
                print("This ones first entry should be {0}: ".format(expected_result))
                print("                                {0}: ".format(all_results), "[{0}]".format(Helpers.get_con_ok(expected_result[0]==all_results[0])))
        print("All clock cycles: ", results[0][Helpers.CONST__AfterKernel][Helpers.CONST__ClkOut1])

    @staticmethod
    def process_output_multi_kernel_w_loop_results(results:typing.List[typing.List[typing.Dict]], max_expected_cycles:int, file_obj:typing.IO[str]|None=None, colored=True):
        def c_format(input:str, color:str, on_color:str|None=None, attrs=[]):
            if colored: return tc.colored(text=input, color=color, on_color=on_color, attrs=attrs)
            else: return input

        print(c_format("Process output for multi-kernel test run...", 'yellow', attrs=['bold']), file=file_obj)
        print(c_format("===========================================", 'yellow', attrs=['bold']), file=file_obj)
        
        for bin_index, bin_file_loop in enumerate(results):
            print(c_format(65*"=", color='green'), file=file_obj)
            print("Filename:", c_format(bin_file_loop[0][Helpers.CONST__Filename], 'green'), "KernelCount:", c_format(bin_file_loop[0][Helpers.CONST__UsedKernelCount], color='green'), "/", bin_file_loop[0][Helpers.CONST__KernelCount], file=file_obj)
            print(c_format(65*"=", color='green'), file=file_obj)
            for outer_loop_index, bin_file in enumerate(bin_file_loop):
                kernels = bin_file[Helpers.CONST__Results]
                # Invariant
                if not (bin_file[Helpers.CONST__UsedKernelCount] == len(kernels)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
                for kernel_index, kk in enumerate(kernels):
                    kk_results = kk[Helpers.CONST__Results]
                    # Output the kernel index and which class it tests
                    print_res = []
                    inner_loop_count = len(kk_results)
                    has_err = False
                    for inner_loop_index, inner_loop in enumerate(kk_results):    
                        bfk_control = inner_loop[Helpers.CONST__BeforeKernel][Helpers.CONST__Control]
                        bfk_uiinput = inner_loop[Helpers.CONST__BeforeKernel][Helpers.CONST__UiInput]
                        bfk_dinput = inner_loop[Helpers.CONST__BeforeKernel][Helpers.CONST__DInput]
                        bfk_uioutput = inner_loop[Helpers.CONST__BeforeKernel][Helpers.CONST__UiOutput]
                        bfk_doutput = inner_loop[Helpers.CONST__BeforeKernel][Helpers.CONST__DOutput]
                        bfk_foutput = inner_loop[Helpers.CONST__BeforeKernel][Helpers.CONST__FOutput]
                        bfk_clkout1 = inner_loop[Helpers.CONST__BeforeKernel][Helpers.CONST__ClkOut1]

                        afk_control = inner_loop[Helpers.CONST__AfterKernel][Helpers.CONST__Control]
                        afk_uiinput = inner_loop[Helpers.CONST__AfterKernel][Helpers.CONST__UiInput]
                        afk_dinput = inner_loop[Helpers.CONST__AfterKernel][Helpers.CONST__DInput]
                        afk_uioutput = inner_loop[Helpers.CONST__AfterKernel][Helpers.CONST__UiOutput]
                        afk_doutput = inner_loop[Helpers.CONST__AfterKernel][Helpers.CONST__DOutput]
                        afk_foutput = inner_loop[Helpers.CONST__AfterKernel][Helpers.CONST__FOutput]
                        afk_clkout1 = inner_loop[Helpers.CONST__AfterKernel][Helpers.CONST__ClkOut1]

                        pprint_res = ["      Inner Loop [{0}/{1}]".format(inner_loop_index+1, inner_loop_count)]
                        cuda_err = inner_loop[Helpers.CONST__CUDAError]
                        if cuda_err or any(k>max_expected_cycles for k in afk_clkout1) or afk_control[0] != 815 or afk_control[1] != afk_control[2] or afk_control[2] != inner_loop_count or afk_control[4] != kernel_index:
                            if cuda_err: pprint_res.append("\n          " + c_format(cuda_err, color='red', attrs=['bold']))
                            pprint_res.append("\n          " + c_format(str(afk_clkout1), color='red'))
                            pprint_res.append("\n           - last measured clock: {0}".format(afk_control[3]))
                            pprint_res.append("\n          " + c_format(str(afk_control), color='red'))
                            has_err = True
                        else:
                            pprint_res.append("         " + str(afk_clkout1) + " - last measured clock: {0}".format(afk_control[3]))
                        print_res.append(pprint_res)

                    class_name = kk[Helpers.CONST__EncVals].split('=')[0].strip()
                    if has_err:
                        misc_str = "   Outer Loop [{0}/{1}] - {2}[{3}-real[{4}]-/{5}]:".format(
                            outer_loop_index+1, 
                            len(bin_file_loop), 
                            c_format('Kernel_', color='red'), 
                            c_format(str(kernel_index), color='red'), 
                            c_format(str(afk_control[4]), color='magenta'), 
                            len(kernels)-1)
                        print_res = [[misc_str, c_format(class_name, color='white', on_color='on_red', attrs=['bold'])]] + print_res
                    else:
                        misc_str = "   Outer Loop [{0}/{1}] - {2}[{3}-real[{4}]-/{5}]:".format(
                            outer_loop_index+1, 
                            len(bin_file_loop), 
                            c_format('Kernel_', color='green'), 
                            c_format(str(kernel_index), color='green'), 
                            c_format(str(afk_control[4]), color='magenta'), 
                            len(kernels)-1)
                        print_res = [[misc_str, c_format(class_name, color='blue', on_color='on_green', attrs=['bold'])]] + print_res

                    print("\n".join([" ".join(x) for x in print_res]), file=file_obj)
    
    @staticmethod
    def overwrite_helper(self, val:tuple|int|bool, val_str:str, enc_vals:dict):
        if isinstance(val, tuple): v = val[-1]
        elif isinstance(val, int): v = val
        elif isinstance(val, bool): v = int(val)
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)
        v_old:SASS_Bits = enc_vals[val_str]
        v_new:SASS_Bits = SASS_Bits.from_int(v, bit_len=v_old.bit_len, signed=v_old.signed)
        enc_vals[val_str] = v_new
        return enc_vals
