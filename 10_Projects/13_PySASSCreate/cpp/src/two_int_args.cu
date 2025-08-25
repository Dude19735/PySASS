#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <format>
#include <vector>
#include <stdint.h>
#include <stdio.h>

/**
 * ===========================================================================================================
 * This kernel has two integer parameters
 * ===========================================================================================================
 * Use it for the tutorial that uses two integer arguments to showcase alignment
 */

// __global__ void kernelT() {
__global__ void 
kernelT1(unsigned int a, unsigned int b) {
    printf("param a=%u, param b=%u\n", a, b);
    return;
}

__global__ void 
kernelT2(unsigned int a, unsigned int* b) {
    printf("param a=%u, param b=%u\n", a, *b);
    return;
}

__global__ void 
kernelT3(unsigned int* a, unsigned int b, unsigned int c) {
    printf("param a=%u, param b=%u, param c=%u\n", *a, b, c);
    return;
}

int main(int argc, char** argv){
    std::string fn = std::string(argv[0]);
    int split_ind = fn.find_last_of("/\\") + 1;
    std::string path = fn.substr(0,split_ind);
    std::string filename = fn.substr(split_ind);

    if(argc != 3){
        std::cout << std::vformat("{0} [a] [b]", std::make_format_args(fn)) << std::endl;
        return 0;
    }
    unsigned int a = static_cast<unsigned int>(std::stoi(argv[1]));
    unsigned int b = static_cast<unsigned int>(std::stoi(argv[2]));

    kernelT1<<<1,1>>>(a, b);
    cudaDeviceSynchronize();
    kernelT2<<<1,1>>>(a, &b);
    cudaDeviceSynchronize();
    kernelT3<<<1,1>>>(&a, b, 3);
    cudaDeviceSynchronize();

    return 0;
}