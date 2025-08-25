#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <format>
#include <vector>
#include <stdint.h>

/**
 * ===========================================================================================================
 * This kernel can be used as template that produces around 60 (SM 70 to 86) to 75 (SM 90 to 120) instructions
 * ===========================================================================================================
 * Number of instructions can be modulated a little bit by setting
 *  - #pragma unroll 1 => fewest instructions
 *  - #pragma unroll 2 => around 60 to 75 instructions
 *  -  ...             => more than 60 to 75 instructions
 * 
 * NOTE: check out the template generator for the stuff that is actually being used!
 */

// __global__ void kernelT() {
__global__ void 
kernelT(unsigned int a, uint64_t *control, uint64_t *ui_output, double* d_output, uint64_t* ui_input, double* d_input, uint64_t *clk_out_1, float* f_output) {
    // #pragma unroll 1
    // for(unsigned int i=0; i<a; ++i){
    //     int64_t t1 = clock64();
    //     int64_t t2 = clock64();
    //     f_output[i] = static_cast<float>(a * (static_cast<float>(t2-t1) + 1.256f));
    // }
    ui_output[0] = ui_input[0] / a;
    // d_output[0] = static_cast<double>(ui_input[0]) / static_cast<double>(a);
    return;
}

int run_test(void* kernel_ptr, int input, int loop_count, const std::string filename, const std::string enc_vals){
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
        std::vector<float> f_output(printout);
        std::vector<uint64_t> ui_input(printout);
        std::vector<double> d_input(printout);
        std::vector<uint64_t> clk_out_1(printout);
        for(int i=0; i<control.size(); ++i) control[i] = i+100;
        for(int i=0; i<ui_output.size(); ++i) ui_output[i] = i+1001;
        for(int i=0; i<d_output.size(); ++i) d_output[i] = static_cast<double>(i)+2001.2;
        for(int i=0; i<f_output.size(); ++i) f_output[i] = static_cast<float>(i)+3001.3;
        for(int i=0; i<ui_input.size(); ++i) ui_input[i] = 0;
        for(int i=0; i<d_input.size(); ++i) d_input[i] = 0.0;
        for(int i=0; i<clk_out_1.size(); ++i) clk_out_1[i] = 999999998;

        // print enc vals
        std::cout << "[EncVals]" << std::endl;
        std::cout << enc_vals << std::endl;
        std::cout << "[/EncVals]" << std::endl;

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

        std::cout << " + [FO] Before kernel " << filename << std::endl << "       finished: f_output(f)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [FOutput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << f_output[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/FOutput]" << std::endl;

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

        std::cout << " + [C1] Before kernel " << filename << std::endl << "       finished: clk_out_1(i)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [ClkOut1]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << clk_out_1[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/ClkOut1]" << std::endl;

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

        float* device_f_output;
        cudaMalloc(&device_f_output, f_output.size()*sizeof(float));
        cudaMemcpy(device_f_output, f_output.data(), f_output.size()*sizeof(float), cudaMemcpyHostToDevice);

        uint64_t* device_ui_input;
        cudaMalloc(&device_ui_input, ui_input.size()*sizeof(uint64_t));
        cudaMemcpy(device_ui_input, ui_input.data(), ui_input.size()*sizeof(uint64_t), cudaMemcpyHostToDevice);

        double* device_d_input;
        cudaMalloc(&device_d_input, d_input.size()*sizeof(double));
        cudaMemcpy(device_d_input, d_input.data(), d_input.size()*sizeof(double), cudaMemcpyHostToDevice);

        uint64_t* device_clk_out_1;
        cudaMalloc(&device_clk_out_1, clk_out_1.size()*sizeof(uint64_t));
        cudaMemcpy(device_clk_out_1, clk_out_1.data(), clk_out_1.size()*sizeof(uint64_t), cudaMemcpyHostToDevice);

        std::cout << "[/BeforeKernel]" << std::endl;
        // ==================================================================================================
        // Run Kernel
        // ==================================================================================================
        // kernelT<<<1,1>>>(input, device_control, device_ui_output, device_d_output, device_ui_input, device_d_input, device_clk_out_1, device_f_output);
        void* args[] = {&input, &device_control, &device_ui_output, &device_d_output, &device_ui_input, &device_d_input, &device_clk_out_1, &device_f_output};
        cudaLaunchKernel(kernel_ptr, 1, 1, args, 0, nullptr);

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
        cudaMemcpy(f_output.data(), device_f_output, f_output.size()*sizeof(float), cudaMemcpyDeviceToHost);
        cudaMemcpy(ui_input.data(), device_ui_input, ui_input.size()*sizeof(uint64_t), cudaMemcpyDeviceToHost);
        cudaMemcpy(d_input.data(), device_d_input, d_input.size()*sizeof(double), cudaMemcpyDeviceToHost);
        cudaMemcpy(clk_out_1.data(), device_clk_out_1, clk_out_1.size()*sizeof(uint64_t), cudaMemcpyDeviceToHost);
        cudaFree(device_control);
        cudaFree(device_ui_output);
        cudaFree(device_d_output);
        cudaFree(device_f_output);
        cudaFree(device_ui_input);
        cudaFree(device_d_input);
        cudaFree(device_clk_out_1);

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

        std::cout << " + [F] After kernel " << filename << std::endl << "       finished: f_output(f)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [FOutput]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << f_output[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/FOutput]" << std::endl;

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

        std::cout << " + [C1] After kernel " << filename << std::endl << "       finished: clk_out_1(i)[";
        for(int i=0; i<printout; ++i) {
            std::cout << i;
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "] = [ClkOut1]" << std::endl << "                   ";
        for(int i=0; i<printout; ++i){
            std::cout << clk_out_1[i];
            if(i<(printout-1)) std::cout << ", ";
        }
        std::cout << "[/ClkOut1]" << std::endl;

        std::cout <<" + [.][After kernel] [UiInput0]" << ui_input[0] << "[/UiInput0], [DInput0]" << d_input[0] << "[/DInput0]" << std::endl;
        std::cout << "[/AfterKernel]" << std::endl;

        std::cout << "[/LoopCount_" << lp << "]" << std::endl;
    }

    return 0;
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

    run_test(reinterpret_cast<void*>(&kernelT), input, loop_count, filename, "");

    return 0;
}