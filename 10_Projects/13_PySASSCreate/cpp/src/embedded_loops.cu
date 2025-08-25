#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <format>
#include <vector>
#include <stdint.h>

/**
 * =======================================================================================================
 * This kernel is used as template that produces a lot of instructions using a lot of registers.
 * 
 * For custom cuda kernels, it is necessary to use a larger non-custom cuda kernel because the number of 
 * registers, that can be used, the amount of shared memory and just the space the compiled cuda kernel
 * takes inside the regular binary, are written into the binary.
 * 
 * Producing a custom cuda kernel from scratch will require writing all those values in the correct place
 * everywhere which then requires knowing exactly how to embed a cuda kernel inside a regular binary too.
 * 
 * These things are probably all documented somewhere, probably, partially inside of some people's heads.
 * =======================================================================================================
 * 
 * As opposed to sample_xdinstr_template.cu, this one also uses a 'double* d_output'. Using doubles introduces
 * a lot of floating point instructions into the kernel.
 * 
 * Using the 'output' pointer and reading from it with offsets into variables that are all seemingly
 * dependent on one another, produces a lot of registers. Since the compiler doesn't know what 'output'
 * is exactly, it can't optimize it away.
 * 
 * The for-loops without '#pragma unroll 1' just produce a lot of instructions, because the compiler will
 * unroll the loops a little bit, trading instruction space for less iterations.
 */

// __global__ void kernelT() {
__global__ void 
kernelT(unsigned int a, uint64_t *control, uint64_t *ui_output, double* d_output, uint64_t* ui_input, double* d_input) {
    if(a > 0x2710) return;

    // Leave this code be because it produces a lot of instructions that can be overwritten
    uint64_t b0 = static_cast<uint64_t>(a);
    uint64_t b1 = ui_output[0] + 1;
    uint64_t b2 = ui_output[1] + 1;
    uint64_t b3 = ui_output[2] + 1;

    uint64_t res4 = 0;
    for(uint64_t j=0; j<b2; ++j){
        int64_t t43 = clock64();
        int64_t t44 = clock64();
        res4 += 3UL*static_cast<uint64_t>(t44 - t43);
        if(b2 > 0x80 && j > 0x60) break;
    }
    d_output[0] = static_cast<double>(res4);

    uint64_t res5 = 0;
    for(uint64_t j=0; j<b2; ++j){
        int64_t t53 = clock64();
        int64_t t54 = clock64();
        res5 += static_cast<uint64_t>(t54 - t53);
        if(b2 > 0x90 && j > 0x70) return;
    }
    d_output[1] = static_cast<double>(res5);

    // outer loop ========>
    int64_t t0 = clock64();
    #pragma unroll 1
    for(uint64_t i=0; i<b0; ++i){
        // nested loop 1 ========>
        uint64_t res1 = 0;
        int64_t t11 = clock64();
        #pragma unroll 1
        for(uint64_t j=0; j<b1; ++j){
            int64_t t13 = clock64();
            // nested-nested loop 3 ========>
            uint64_t res3 = 0;
            int64_t t31 = clock64();
            #pragma unroll 1
            for(uint64_t x=0; x<b3; ++x){
                int64_t t33 = clock64();
                int64_t t34 = clock64();
                res3 += static_cast<uint64_t>(t34 - t33);
            }
            int64_t t32 = clock64();
            ui_output[i+3] = res3 + static_cast<uint64_t>((static_cast<float>(t32-t31) + 1.358f));
            // ========> nested-nested loop 3

            int64_t t14 = clock64();
            res1 += static_cast<uint64_t>(t14 - t13);
        }
        int64_t t12 = clock64();
        ui_output[i+1] = res1 + static_cast<uint64_t>((static_cast<float>(t12-t11) + 1.256f));
        // ========> nested loop 1

        if(a < 10) return;

        // nested loop 2 ========>
        uint64_t b2 = res1 + 1;
        uint64_t res2 = 0;
        int64_t t21 = clock64();
        #pragma unroll 1
        for(uint64_t j=0; j<b2; ++j){
            int64_t t23 = clock64();
            int64_t t24 = clock64();
            res2 += static_cast<uint64_t>(t24 - t24);
        }
        int64_t t22 = clock64();
        ui_output[i+2] = res2 + static_cast<uint64_t>((static_cast<float>(t22-t21) + 1.2869f));
        // ========> nested loop 2
    }
    int64_t t3 = clock64();
    ui_output[0] = static_cast<int>(a * (static_cast<float>(t3-t0) + 1.28964f*static_cast<float>(a)));
    // ========> outer loop

    return;
}

int main(int argc, char** argv){
    std::string fn = std::string(argv[0]);
    int split_ind = fn.find_last_of("/\\") + 1;
    std::string path = fn.substr(0,split_ind);
    std::string filename = fn.substr(split_ind);

    if(argc != 2){
        std::cout << std::vformat("{0} [input]", std::make_format_args(fn)) << std::endl;
        return 0;
    }
    unsigned int input = static_cast<unsigned int>(std::stoi(argv[1]));
    std::cout << "[Filename]" << filename << "[/Filename] [Input]" << input << "[/Input]" << std::endl;

    int loop_count = (input == 0) ? input++ : input;

    for(int lp=0; lp<loop_count; ++lp){
        std::cout << "[LoopCount_" << lp << "]" << std::endl;
        // ==================================================================================================
        // Define input data
        // ==================================================================================================
        int control_size = 15;
        int printout = loop_count;
        std::vector<uint64_t> control(control_size);
        std::vector<uint64_t> ui_output(printout);
        std::vector<double> d_output(printout);
        std::vector<uint64_t> ui_input(printout);
        std::vector<double> d_input(printout);
        for(int i=0; i<control.size(); ++i) control[i] = i+100;
        for(int i=0; i<ui_output.size(); ++i) ui_output[i] = i+1001;
        for(int i=0; i<d_output.size(); ++i) d_output[i] = static_cast<double>(i)+2001.2;
        for(int i=0; i<ui_input.size(); ++i) ui_input[i] = 0;
        for(int i=0; i<d_input.size(); ++i) d_input[i] = 0.0;

        // ==================================================================================================
        // Print input data
        // ==================================================================================================
        std::cout << "[BeforeKernel]" << std::endl;
        std::cout << " + [C] Before kernel " << filename << std::endl << "       finished: control(i)[";
        for(int i=0; i<control_size; ++i) {
            std::cout << i;
            if(i<(control_size-1)) std::cout << ", ";
        }
        std::cout << "] = [Control]" << std::endl << "                   ";
        for(int i=0; i<control_size; ++i){
            std::cout << control[i];
            if(i<(control_size-1)) std::cout << ", ";
        }
        std::cout << "[/Control]" << std::endl;

        std::cout << " + [IO] Before kernel " << filename << std::endl << "       finished: ui_output(i)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [UiOutput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << ui_output[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/UiOutput]" << std::endl;

        std::cout << " + [DO] Before kernel " << filename << std::endl << "       finished: d_output(d)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [DOutput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << d_output[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/DOutput]" << std::endl;

        std::cout << " + [II] Before kernel " << filename << std::endl << "       finished: ui_input(i)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [UiInput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << ui_input[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/UiInput]" << std::endl;

        std::cout << " + [DI] Before kernel " << filename << std::endl << "       finished: d_input(d)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [DInput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << d_input[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/DInput]" << std::endl;

        std::cout <<" + [.][Before kernel] [UiInput0]" << ui_input[0] << "[/UiInput0], [DInput0]" << d_input[0] << "[/DInput0]" << std::endl;

        // ==================================================================================================
        // Copy input data to GPU
        // ==================================================================================================
        uint64_t* device_control;
        cudaMalloc(&device_control, control.size()*sizeof(uint64_t));
        cudaMemcpy(device_control, control.data(), control.size()*sizeof(uint64_t), cudaMemcpyHostToDevice);

        uint64_t* device_ui_output;
        cudaMalloc(&device_ui_output, ui_output.size()*sizeof(uint64_t));
        cudaMemcpy(device_ui_output, ui_output.data(), ui_output.size()*sizeof(uint64_t), cudaMemcpyHostToDevice);

        double* device_d_output;
        cudaMalloc(&device_d_output, d_output.size()*sizeof(double));
        cudaMemcpy(device_d_output, d_output.data(), d_output.size()*sizeof(double), cudaMemcpyHostToDevice);

        uint64_t* device_ui_input;
        cudaMalloc(&device_ui_input, ui_input.size()*sizeof(uint64_t));
        cudaMemcpy(device_ui_input, ui_input.data(), ui_input.size()*sizeof(uint64_t), cudaMemcpyHostToDevice);

        double* device_d_input;
        cudaMalloc(&device_d_input, d_input.size()*sizeof(double));
        cudaMemcpy(device_d_input, d_input.data(), d_input.size()*sizeof(double), cudaMemcpyHostToDevice);

        std::cout << "[/BeforeKernel]" << std::endl;
        // ==================================================================================================
        // Run Kernel
        // ==================================================================================================
        kernelT<<<1,1>>>(input, device_control, device_ui_output, device_d_output, device_ui_input, device_d_input);

        cudaDeviceSynchronize();
        cudaError_t err = cudaGetLastError();
        if ( err != cudaSuccess ) {
            std::cout << "[CUDAError]" << cudaGetErrorString(err) << "[/CUDAError]" << std::endl;
        }

        std::cout << "[AfterKernel]" << std::endl;

        // ==================================================================================================
        // Copy output data to CPU
        // ==================================================================================================
        cudaMemcpy(control.data(), device_control, control.size()*sizeof(uint64_t), cudaMemcpyDeviceToHost);
        cudaMemcpy(ui_output.data(), device_ui_output, ui_output.size()*sizeof(uint64_t), cudaMemcpyDeviceToHost);
        cudaMemcpy(d_output.data(), device_d_output, d_output.size()*sizeof(double), cudaMemcpyDeviceToHost);
        cudaMemcpy(ui_input.data(), device_ui_input, ui_input.size()*sizeof(uint64_t), cudaMemcpyDeviceToHost);
        cudaMemcpy(d_input.data(), device_d_input, d_input.size()*sizeof(double), cudaMemcpyDeviceToHost);
        cudaFree(device_control);
        cudaFree(device_ui_output);
        cudaFree(device_d_output);
        cudaFree(device_ui_input);
        cudaFree(device_d_input);

        // ==================================================================================================
        // Print output data
        // ==================================================================================================
        std::cout << " + [C] After kernel " << filename << std::endl << "       finished: control(i)[";
        for(int i=0; i<control_size; ++i) {
            std::cout << i;
            if(i<(control_size-1)) std::cout << ", ";
        }
        std::cout << "] = [Control]" << std::endl << "                   ";
        for(int i=0; i<control_size; ++i){
            std::cout << control[i];
            if(i<(control_size-1)) std::cout << ", ";
        }
        std::cout << "[/Control]" << std::endl;

        std::cout << " + [I] After kernel " << filename << std::endl << "       finished: ui_output(i)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [UiOutput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << ui_output[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/UiOutput]" << std::endl;

        std::cout << " + [D] After kernel " << filename << std::endl << "       finished: d_output(d)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [DOutput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << d_output[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/DOutput]" << std::endl;

        std::cout << " + [II] After kernel " << filename << std::endl << "       finished: ui_input(i)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [UiInput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << ui_input[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/UiInput]" << std::endl;

        std::cout << " + [DI] After kernel " << filename << std::endl << "       finished: d_input(d)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [DInput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << d_input[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/DInput]" << std::endl;

        std::cout <<" + [.][After kernel] [UiInput0]" << ui_input[0] << "[/UiInput0], [DInput0]" << d_input[0] << "[/DInput0]" << std::endl;
        std::cout << "[/AfterKernel]" << std::endl;

        std::cout << "[/LoopCount_" << lp << "]" << std::endl;
    }

    return 0;
}