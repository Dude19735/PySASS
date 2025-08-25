#include <stdexcept>
#include "stdint.h"
#include "math.h"

// Find the value where (floor <= res <= max_val) and (res & mask == 0)
// floor = N1, max_val = N2, mask = B
// (for unsigned cases to make sure all comparisons work)
static uint64_t next_best_u(uint64_t floor, uint64_t max_val, uint64_t mask, bool& success){
    success = false;
    uint64_t i;
    uint64_t res = floor;
    uint64_t res2 = floor;
    if((floor & mask) != 0){
        if(floor == mask)
            res = 1 << static_cast<uint64_t>(std::floor(std::log2(floor) + 1.f));
        else {
            i = 0;
            while(res <= floor && floor <= max_val){
                res = (((floor+i) | mask) + 1) & (~mask);
                ++i;
                // if(i > 1000) throw std::runtime_error("Unexpected: too many iterations");
            }
        }

        int iiv = (63 - __builtin_clzll(floor & mask));
        const uint64_t ll = 1UL<<iiv;
        res2 = ((floor | mask) + (floor & ll)) & (~mask);
        res2 &= ~(ll - 1);
    }
    
    if(res2 != res) throw std::runtime_error("Unexpected");

    if(res <= max_val) success = true;
    return res;
}

// Find the value where (min_val <= res <= ceil) and (res & mask == 0)
// min_val = N1, ceil = N2, mask = B
// (for unsigned cases to make sure all comparisons work)
// There is only an unsigned version for this one because N2 is always >= 0 and if
// there is a mask != 0, 0 will always work. If N1 > 0 as well, the unsigned case
// still works
static uint64_t previous_best_u(uint64_t ceil, uint64_t min_val, uint64_t mask, bool& success){
    uint64_t res = ceil;
    uint64_t res2 = ceil;
    uint64_t i;
    success = false;
    if((ceil & mask) != 0){
        uint64_t floor = (ceil & ~mask);
        
        i = 0;
        res = floor;
        uint64_t next = res;
        while(next <= ceil){
            res = next;
            next = (((floor+i) | mask) + 1) & (~mask);
            ++i;
            // if(i > 1000) throw std::runtime_error("Unexpected: too many iterations");
        }

        res2 = floor;
        uint64_t iiv = 63 - __builtin_clzll(ceil & mask);
        uint64_t nmask = ~mask & ((1UL<<iiv)-1);
        res2 |= nmask;
    }

    if(res2 != res) throw std::runtime_error("Unexpected");

    if(res >= min_val) success = true;
    return res;
}

// Find the value where (floor <= res <= max_val) and (res & mask == 0)
// floor = N1, max_val = N2, mask = B
// (for signed cases to make sure all comparisons work)
static int64_t next_best_s(int64_t floor, int64_t max_val, uint64_t mask, bool& success){
    success = false;
    int64_t i;
    int64_t res = floor;
    int64_t res2 = floor;
    if((floor & mask) != 0){
        if(floor == mask) 
            res = 1 << static_cast<int64_t>(std::floor(std::log2(floor) + 1.f));
        else {
            i = 0;
            while(res <= floor && floor <= max_val){
                res = (((floor+i) | mask) + 1) & (~mask);
                ++i;
                // if(i > 1000) throw std::runtime_error("Unexpected: too many iterations");
            }
        }

        int iiv = (63 - __builtin_clzll(floor & mask));
        const uint64_t ll = 1UL<<iiv;
        res2 = ((floor | mask) + (floor & ll)) & (~mask);
        res2 &= ~(ll - 1);
    }

    if(res2 != res) throw std::runtime_error("Unexpected");

    if(res <= max_val) success = true;
    return res;
}

void test_next_best(){
    uint8_t bit_len = 13;
    uint64_t bit_mask_start = 0;
    uint64_t bit_mask_max = 8191;

    uint64_t max_val_u = static_cast<uint64_t>(std::pow(2, bit_len)-1);
    for(uint64_t bit_mask = bit_mask_start; bit_mask<=bit_mask_max; ++bit_mask) {
        for(uint64_t min_val = 0; min_val < max_val_u; ++min_val){
            if(bit_mask == 1024 && min_val == 1025){
                int x = 5;
            }
            bool success;
            uint64_t res = next_best_u(min_val, max_val_u, bit_mask, success);
            bool cond1 = (res & bit_mask) == 0;
            bool cond2 = res >= min_val;
            bool cond3 = res <= max_val_u || !success;
            if(!cond1 || !cond2 || !cond3) throw std::runtime_error("Unexpected");

            // we got the result.
            // if any of the intermediate numbers also works... not good...
            if(min_val > 0 && bit_mask > 0){
                --res;
                while(res >= min_val){
                    bool cond = (res & bit_mask) == 0;
                    if(cond) throw std::runtime_error("Unexpected");
                    --res;
                }
            }
        }
    }

    int64_t max_val_s = static_cast<uint64_t>(std::pow(2, bit_len-1)-1);
    for(uint64_t bit_mask = bit_mask_start; bit_mask<=bit_mask_max; ++bit_mask) {
        for(int64_t min_val = -max_val_s; min_val < max_val_s; ++min_val){
            bool success;
            int64_t res = static_cast<int64_t>(next_best_s(min_val, max_val_s, bit_mask, success));
            bool cond1 = (res & bit_mask) == 0;
            bool cond2 = res >= min_val;
            bool cond3 = res <= max_val_s || !success;
            if(!cond1 || !cond2 || !cond3) throw std::runtime_error("Unexpected");

            // we got the result.
            // if any of the intermediate numbers also works... not good...
            if(bit_mask > 0){
                --res;
                while(res >= min_val){
                    bool cond = (res & bit_mask) == 0;
                    if(cond) throw std::runtime_error("Unexpected");
                    --res;
                }
            }
        }
    }
}

void test_previous_best(){
    uint8_t bit_len = 12;
    uint64_t bit_mask_start = 0;
    uint64_t bit_mask_max = 4095;

    uint64_t n2;
    uint64_t i_u;
    bool success;

    uint64_t min_val_u = 0;
    uint64_t max_val_u = static_cast<uint64_t>(std::pow(2, bit_len)-1);
    for(uint64_t bit_mask = bit_mask_start; bit_mask<=bit_mask_max; ++bit_mask) {
        for(uint64_t max_val = max_val_u; max_val >= 0; --max_val){
            bool success1;
            bool success2;
            uint64_t res = previous_best_u(max_val, min_val_u, bit_mask, success2);
            bool cond1 = (res & bit_mask) == 0;
            bool cond2 = res <= max_val;
            bool cond3 = res >= min_val_u;
            if(!cond1 || !cond2 || !cond3) throw std::runtime_error("Unexpected");

            // we got the result.
            // if any of the intermediate numbers also works... not good...
            uint64_t rr = res;
            if(max_val > 0 && bit_mask > 0){
                ++rr;
                while(rr <= max_val){
                    bool cond = (rr & bit_mask) == 0;
                    if(cond) throw std::runtime_error("Unexpected");
                    ++rr;
                }
            }

            if(max_val == 0) break;
        }
    }
}

int main(int argc, char** argv){
    // uint64_t floor = 1025;
    // uint64_t max_val = 3000;
    // uint64_t bit_mask = 1024;
    // bool success;
    // uint64_t n2 = next_best_u(floor, max_val, bit_mask, success);

    // test_next_best();
    test_previous_best();
    // bool success;
    // uint64_t res = previous_best_u(4089, 0, 5, success);
    // uint64_t res = previous_best_u(250, 0, 10, success);
    return 0;
}