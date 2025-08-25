#include <bitset>
#include <type_traits>
#include <iostream>
#include <fstream>
#include <cmath>
#include <assert.h>
#include <iomanip>
#include <set>
#include "../src/SASS_Bits.hpp"
#include "../src/SASS_Range_Lib.hpp"
#include "../src/SASS_Range.hpp"
#include "../src/SASS_Range_Iter.hpp"
#include "../src/SASS_Enc_Dom.hpp"

template<typename T>
std::enable_if_t<std::is_integral_v<T>,std::string>
encode_binary(T i){
    return std::bitset<sizeof(T) * 8>(i).to_string();
}

void test_range_intersection(int sign){
    std::vector<SASS::SASS_Bits> l;
    for(int i=0; i<10; ++i)
        l.push_back(SASS::SASS_Bits::from_int(i));

    std::set<SASS::SASS_Bits> s;
    for(int i=0; i<10; ++i)
        s.insert(l[i]);

    auto rr1 = SASS::SASS_Range(1, 0, 8, sign, 3);
    auto res = SASS::SASS_Range::intersection_s(rr1, s);
    res.erase(l[0]);
    res.erase(l[4]);
    res.erase(l[8]);
    assert(res.size() == 0);

    auto rr2 = SASS::SASS_Range(1, 0, 8, sign, 3);
    auto rr3 = SASS::SASS_Range::intersection_r(rr1, rr2);
    assert(SASS::SASS_Range::size(rr2) == SASS::SASS_Range::size(rr1));
    assert(SASS::SASS_Range::size(rr1) == SASS::SASS_Range::size(rr3));
    assert(rr1 == rr2);
    assert(rr1 == rr3);
    bool finished = false;
    std::set<SASS::SASS_Bits> mres;
    uint64_t counter = 0;
    auto iter = SASS::SASS_Range::__iter__(rr3);
    while(!finished){
        const auto& val = iter.__next__(finished);
        if(!finished){
            assert(SASS::SASS_Range::__contains__(rr3, val) == true);
            assert(SASS::SASS_Range::__contains__(rr1, val) == true);
            assert(SASS::SASS_Range::__contains__(rr2, val) == true);
            mres.insert(val);
            counter++;
        }
    }

    finished = false;
    auto iter2 = SASS::SASS_Range::__iter__(rr3);
    while(!finished){
        const auto& val = iter2.__next__(finished);
        if(!finished){
            assert(mres.contains(val) == true);
            mres.erase(val);
        }
    }
    assert(mres.size() == 0);

    auto rr4 = SASS::SASS_Range(1, 0, 8, sign, 12);
    auto rr5 = SASS::SASS_Range::intersection_r(rr1, rr4);
    auto size = SASS::SASS_Range::size(rr5);
    assert(size == 16);
    assert(SASS::SASS_Range::__max__(rr5) == SASS::SASS_Range::__max__(rr1));
    assert(SASS::SASS_Range::__max__(rr5) == SASS::SASS_Range::__max__(rr4));
    assert(SASS::SASS_Range::__min__(rr5) == SASS::SASS_Range::__min__(rr1));
    assert(SASS::SASS_Range::__min__(rr5) == SASS::SASS_Range::__min__(rr4));

    std::set<SASS::SASS_Bits> s2;
    for(int i=0; i<256; ++i){
        if((i & 15) == 0){
            std::cout << i << " " << (i & 15) << " " << (i>>4) << std::endl;
            if(sign==1) s2.insert(SASS::SASS_Bits::from_int(i-128, 0, sign));
            else s2.insert(SASS::SASS_Bits::from_int(i, 0, sign));
        }
    }
    assert(s2.size() == 16);
    
    auto iter3 = SASS::SASS_Range::__iter__(rr5);
    finished = false;
    while(!finished){
        const auto& val = iter3.__next__(finished);
        if(!finished){
            assert(s2.contains(val) == true);
            s2.erase(val);
        }
    }
    assert(s2.size() == 0);
}

void test_range_intersection_2(){
    // SASS_Range and set<SASS_Bits>
    std::set<SASS::SASS_Bits> bits;
    for(int i=0; i<100; ++i){
        bits.insert(SASS::SASS_Bits::from_int(i));
    }
    std::set<SASS::SASS_Bits> expected;
    for(int i=50; i<100; ++i){
        expected.insert(SASS::SASS_Bits::from_int(i));
    }

    SASS::SASS_Range r(50, 150, 10, 0, 0);
    auto res = SASS::SASS_Range::intersection_s(r, bits);

    for(const auto& i : res) if(!expected.contains(i)) throw std::runtime_error("Unexpected");
    for(const auto& i : expected) if(!res.contains(i)) throw std::runtime_error("Unexpected");

    // SASS_Range and SASS_Range
    SASS::SASS_Range r2(20, 100, 10, 0, 0);
    auto res2 = SASS::SASS_Range::intersection_r(r, r2);
    std::set<SASS::SASS_Bits> expected2;
    for(int i=50; i<101; ++i){
        expected2.insert(SASS::SASS_Bits::from_int(i));
    }

    std::set<SASS::SASS_Bits> res2_set;
    auto iter = SASS::SASS_Range::__iter__(res2);
    bool finished = false;
    while(!finished){
        auto val = iter.__next__(finished);
        if(!finished) res2_set.insert(val);
    }

    for(const auto& i : expected2) if(!res2_set.contains(i)) throw std::runtime_error("Unexpected");
    for(const auto& i : res2_set) if(!expected2.contains(i)) throw std::runtime_error("Unexpected");

}

void test_size(const SASS::SASS_Range& r, const uint64_t r_size){
    const auto size = SASS::SASS_Range::size(r);
    if(size != r_size) throw std::runtime_error("Unexpected");
}

void test_size_2(const SASS::SASS_Range& r){
    const auto size = SASS::SASS_Range::size(r);
    const int64_t range_min = SASS::SASS_Range::__min__(r);
    const int64_t range_max = static_cast<int64_t>(SASS::SASS_Range::__max__(r));
    const uint64_t bit_mask = r.bit_mask();
    std::set<int64_t> res;
    for(int64_t m=range_min; m <=range_max; ++m){
        if((m & bit_mask) == 0) 
            res.insert(m);
    }
    test_size(r, res.size());
}

void test_size_3_signed(const uint8_t from_bit_len, const uint8_t to_bit_len){
    std::cout << "...signed " << static_cast<int>(from_bit_len) << " to " << static_cast<int>(to_bit_len) << std::endl;
    for(uint8_t bit_len = from_bit_len; bit_len <= to_bit_len; ++bit_len){
        // signed
        int64_t range_min = -static_cast<int64_t>(std::pow(2, bit_len-1)-1);
        int64_t range_max = static_cast<int64_t>(std::pow(2, bit_len-1)-1);
        std::cout << "                                   " << '\r' << "... ..." << static_cast<int>(bit_len) << ": [" << range_min << "," << range_max << "]" << '\r' << std::flush;
        for(int64_t r_min=range_min; r_min <= range_max; r_min++){
            int64_t r_max_min = std::max(static_cast<int64_t>(0), r_min);
            for(int64_t r_max=r_max_min; r_max <= range_max; r_max++){
                for(uint64_t bit_mask=0; bit_mask<=r_max; bit_mask++){
                    SASS::SASS_Range r(r_min, static_cast<uint64_t>(r_max), bit_len, 1, bit_mask);
                    test_size_2(r);
                }
            }
        }
        std::cout << "                                   " << '\r' << "... ..." << static_cast<int>(bit_len) << ": [" << range_min << "," << range_max << "]" << std::endl;
    }
}

void test_size_3_unsigned(const uint8_t from_bit_len, const uint8_t to_bit_len){
    std::cout << "...unsigned " << static_cast<int>(from_bit_len) << " to " << static_cast<int>(to_bit_len) << std::endl;
    for(uint8_t bit_len = from_bit_len; bit_len <= to_bit_len; ++bit_len){
        // unsigned
        uint64_t range_max = static_cast<uint64_t>(std::pow(2, bit_len)-1);
        std::cout << "                                   " << '\r' << "... ..." << static_cast<int>(bit_len) << ": [" << 0 << "," << range_max << "]" << '\r' << std::flush;
        for(int64_t r_min=0; r_min <= range_max; r_min++){
            uint64_t r_max_min = static_cast<uint64_t>(std::max(static_cast<int64_t>(0), r_min));
            for(uint64_t r_max=r_max_min; r_max <= range_max; r_max++){
                for(uint64_t bit_mask=0; bit_mask<=r_max; bit_mask++){
                    SASS::SASS_Range r(r_min, r_max, bit_len, 0, bit_mask);
                    test_size_2(r);
                }
            }
        }
        std::cout << "                                   " << '\r' << "... ..." << static_cast<int>(bit_len) << ": [" << 0 << "," << range_max << "]" << std::endl;
    }
}

void test_size_3(const uint8_t from_bit_len, const uint8_t to_bit_len, bool signed_){
    std::cout << "test size " << static_cast<int>(from_bit_len) << " to " << static_cast<int>(to_bit_len) << std::endl;
    if(signed_){
        // signed
        test_size_3_signed(from_bit_len, to_bit_len);
    }
    else{
        // unsigned
        test_size_3_unsigned(from_bit_len, to_bit_len);
    }
}

void test_range_s(const SASS::SASS_Range& r, const int test_nr) {
    std::set<int64_t> found;
    std::map<int64_t, uint64_t> count;
    std::set<SASS::SASS_Bits> bb_found;
    const auto size = SASS::SASS_Range::size(r);
    std::cout << SASS::SASS_Range::pretty(r) << std::endl;
    if(size == 0) return;
    const int step = 100000;
    for(int i=0; i<test_nr; ++i){
        if(i%step == 0) 
            std::cout << "              " << '\r'  << i << '\r' << std::flush;
        auto val = SASS::SASS_Range::pick(r);
        auto val_int = SASS::SASS_Bits::__int__(val);
        if(!found.contains(val_int)) count.insert({val_int, 1});
        else count.at(val_int)++;
        found.insert(val_int);
        bb_found.insert(val);
    }
    
    double mean = static_cast<double>(test_nr) / static_cast<double>(SASS::SASS_Range::calculate_limits(r).size);
    double var = 0;
    uint64_t min_count = std::numeric_limits<uint64_t>::max();
    uint64_t max_count = 0;
    for(const auto& ii : count){
        var += std::pow(ii.second - mean, 2);
        if(ii.second < min_count) min_count = ii.second;
        if(ii.second > max_count) max_count = ii.second;
    }
    var /= static_cast<double>(test_nr);
    std::cout << test_nr << " (" << mean << " +- " << std::sqrt(var) << " or [" << min_count << "," << max_count  << "])" << std::endl;

    if(found.size() != size) throw std::runtime_error("Unexpected");
    if(bb_found.size() != found.size()) throw std::runtime_error("Unexpected");
    for(const auto& b : bb_found){
        if(SASS::SASS_Range::__contains__(r, b, true) == false) {
            throw std::runtime_error("Unexpected");
        }
    }

    int64_t min_val = SASS::SASS_Range::__min__(r);
    uint64_t max_val = static_cast<int64_t>(SASS::SASS_Range::__max__(r));
    for(int64_t m=min_val; m<=max_val; ++m){
        const auto bb = SASS::SASS_Bits::from_int(m, r.bit_len(), r.signed_());
        if(SASS::SASS_Range::__contains__(r, bb)){
            if(!bb_found.contains(bb)) throw std::runtime_error("Unexpected");
        }
        else {
            if(bb_found.contains(bb)) throw std::runtime_error("Unexpected");
        }
    }
}

void test_range_u(const SASS::SASS_Range& r, const int test_nr) {
    std::set<uint64_t> found;
    std::map<uint64_t, uint64_t> count;
    std::set<SASS::SASS_Bits> bb_found;
    const auto size = SASS::SASS_Range::size(r);
    std::cout << SASS::SASS_Range::pretty(r) << std::endl;
    if(size == 0) return;
    const int step = 200000;
    for(int i=0; i<test_nr; ++i){
        if(i%step == 0) 
            std::cout << "              " << '\r'  << i << '\r' << std::flush;
        auto val = SASS::SASS_Range::pick(r);
        uint64_t val_int = static_cast<uint64_t>(SASS::SASS_Bits::__int__(val));
        if(!found.contains(val_int)) count.insert({val_int, 1});
        else count.at(val_int)++;
        found.insert(val_int);
        bb_found.insert(val);
    }

    // calculate standard deviation
    double mean = static_cast<double>(test_nr) / static_cast<double>(SASS::SASS_Range::calculate_limits(r).size);
    double var = 0;
    uint64_t min_count = std::numeric_limits<uint64_t>::max();
    uint64_t max_count = 0;
    for(const auto& ii : count){
        var += std::pow(ii.second - mean, 2);
        if(ii.second < min_count) min_count = ii.second;
        if(ii.second > max_count) max_count = ii.second;
    }
    var /= static_cast<double>(test_nr);
    std::cout << test_nr << " (" << mean << " +- " << std::sqrt(var) << " or [" << min_count << "," << max_count  << "])" << std::endl;

    if(found.size() != size) throw std::runtime_error("Unexpected");
    if(bb_found.size() != found.size()) throw std::runtime_error("Unexpected");
    for(const auto& b : bb_found){
        if(SASS::SASS_Range::__contains__(r, b, true) == false) {
            throw std::runtime_error("Unexpected");
        }
    }

    uint64_t min_val = static_cast<uint64_t>(SASS::SASS_Range::__min__(r));
    uint64_t max_val = static_cast<int64_t>(SASS::SASS_Range::__max__(r));
    for(uint64_t m=min_val; m<=max_val; ++m){
        const auto bb = SASS::SASS_Bits::from_int(static_cast<int64_t>(m), r.bit_len(), r.signed_());
        if(SASS::SASS_Range::__contains__(r, bb)){
            if(!bb_found.contains(bb)) throw std::runtime_error("Unexpected");
        }
        else {
            if(bb_found.contains(bb)) throw std::runtime_error("Unexpected");
        }
    }
}

void test_range(const SASS::SASS_Range& r, const int test_nr) {
    if(r.signed_()) test_range_s(r, test_nr);
    else test_range_u(r, test_nr);
}

void test_range_2(uint8_t from_bit_len, uint8_t to_bit_len, const int test_nr, bool signed_) {
    std::cout << "Ranges from " << static_cast<int>(from_bit_len) << "B to " << static_cast<int>(to_bit_len) << "B" << std::endl;
    if(signed_ == false){
        for(uint8_t bit_len = from_bit_len; bit_len <= to_bit_len; ++bit_len){
            // unsigned
            uint64_t range_min_u = 0;
            uint64_t range_max_u = static_cast<int64_t>(std::pow(2, bit_len)-1);
            std::cout << "..." << static_cast<int>(bit_len) << "B: [" << range_min_u << "," << range_max_u << "]" << std::endl;
            for(uint64_t r_min=range_min_u; r_min <= range_max_u; r_min++){
                uint64_t r_max_min = std::max(static_cast<uint64_t>(0), r_min);
                for(uint64_t r_max=r_max_min; r_max <= range_max_u; r_max++){
                    for(uint64_t bit_mask=0; bit_mask<=r_max; bit_mask++){
                        SASS::SASS_Range r(static_cast<uint64_t>(r_min), r_max, bit_len, 0, bit_mask);
                        test_range(r, test_nr);
                    }
                }
            }
            std::cout << "-------------------------------------------------------------------------" << std::endl;
        }
    }
    else{
        for(uint8_t bit_len = from_bit_len; bit_len <= to_bit_len; ++bit_len){
            // signed
            int64_t range_min_s = -static_cast<int64_t>(std::pow(2, bit_len-1)-1);
            int64_t range_max_s = static_cast<int64_t>(std::pow(2, bit_len-1)-1);
            std::cout << "..." << static_cast<int>(bit_len) << "B: [" << range_min_s << "," << range_max_s << "]" << std::endl;
            if(bit_len < 2) {
                std::cout << "... ... skip: at least 2 bits for signed necessary" << std::endl;
                continue;
            }
            for(int64_t r_min=range_min_s; r_min <= range_max_s; r_min++){
                int64_t r_max_min = std::max(static_cast<int64_t>(0), r_min);
                for(int64_t r_max=r_max_min; r_max <= range_max_s; r_max++){
                    for(uint64_t bit_mask=0; bit_mask<=r_max; bit_mask++){
                        SASS::SASS_Range r(r_min, static_cast<uint64_t>(r_max), bit_len, 1, bit_mask);
                        test_range(r, test_nr);
                    }
                }
            }
            
            std::cout << "=========================================================================" << std::endl;
        }
    }
    
}

void test_range_iter(int64_t range_min, uint64_t range_max, uint8_t bit_len, uint8_t signed_, uint64_t bit_mask, bool print, bool half=false){
    SASS::SASS_Bits iter_min = SASS::SASS_Bits::from_int(0);
    SASS::SASS_Bits iter_max = SASS::SASS_Bits::from_int(0);
    SASS::SASS_Range r(range_min, range_max, bit_len, signed_, bit_mask);
    bool finished = false;
    if(print) std::cout << "========= " << SASS::SASS_Range::pretty(r);
    if(!SASS::SASS_Range::__iterable__(r)) {
        if(print) std::cout << " => skip" << std::endl;
        return;
    }
    else {
        if(print) std::cout << std::endl;
    }

    auto iter = SASS::SASS_Range::__iter__(r);
    uint64_t counter = 0;
    while(!finished){
        auto val = iter.__next__(finished);
        if(!finished) {
            if(print) std::cout << SASS::SASS_Bits::__str__(val) << std::endl;
            if(counter == 0) iter_min = val;
            iter_max = val;
            counter++;
        }
    }
    if(counter != SASS::SASS_Range::size(r)) throw std::runtime_error("Unexpected");
    if(counter > 0){
        int64_t smallest = SASS::SASS_Bits::__int__(iter_min);
        uint64_t largest = static_cast<uint64_t>(SASS::SASS_Bits::__int__(iter_max));
        if(smallest != r.limits().range_min) throw std::runtime_error("Unexpected");
        if(largest != r.limits().range_max) throw std::runtime_error("Unexpected");
    }
}

void test_range_iter_2(int64_t range_min, uint64_t range_max, uint8_t bit_len, uint8_t signed_, uint64_t bit_mask, uint64_t sample_size, bool print){
    SASS::SASS_Bits iter_min = SASS::SASS_Bits::from_int(0);
    SASS::SASS_Bits iter_max = SASS::SASS_Bits::from_int(0);
    SASS::SASS_Range r(range_min, range_max, bit_len, signed_, bit_mask);
    bool finished = false;
    if(print) std::cout << "========= " << SASS::SASS_Range::pretty(r);
    if(!SASS::SASS_Range::__iterable__(r)) {
        if(print) std::cout << " => [skip]" << std::endl;
        return;
    }
    else {
        if(print) std::cout << " => [sample_size=" << sample_size << "]" << std::endl;
    }

    auto iter = SASS::SASS_Range::__sized_iter__(r, sample_size);
    uint64_t counter = 0;
    while(!finished){
        auto val = iter.__next__(finished);
        if(!finished) {
            if(print) std::cout << SASS::SASS_Bits::__str__(val) << std::endl;
            if(counter == 0) iter_min = val;
            iter_max = val;
            counter++;
        }
        if(counter == std::numeric_limits<uint64_t>::max()-5){
            int x = 5;
        }
    }
    if(!r.limits().size_overflow){
        if(counter != sample_size && SASS::SASS_Range::size(r) >= sample_size) throw std::runtime_error("Unexpected");
        if(counter != SASS::SASS_Range::size(r) && SASS::SASS_Range::size(r) < sample_size) throw std::runtime_error("Unexpected");
    } else {
        if(counter != sample_size) throw std::runtime_error("Unexpected");
    }
    if(counter > 0){
        int64_t smallest = SASS::SASS_Bits::__int__(iter_min);
        uint64_t largest = static_cast<uint64_t>(SASS::SASS_Bits::__int__(iter_max));
        if(smallest != r.limits().range_min) throw std::runtime_error("Unexpected");
        if(largest != r.limits().range_max) throw std::runtime_error("Unexpected");
    }
}

void test_range_iter_3(uint8_t bit_len, bool signed_, bool skip_intermediate=false){
    std::cout << "test_range_iter_3(bit_len == " << static_cast<int>(bit_len) << ", signed=" << signed_ << ")" << std::endl;
    if(!signed_){
        uint64_t range_min_u = 0;
        uint64_t range_max_u = static_cast<uint64_t>((((1UL << (bit_len-1))-1)<<1)+1);
        for(uint64_t r_min=range_min_u; r_min <= range_max_u; r_min++){
            uint64_t r_max_min = std::max(static_cast<uint64_t>(0), r_min);
            if(skip_intermediate) r_max_min = range_max_u;
            for(uint64_t r_max=r_max_min; r_max <= range_max_u; r_max++){
                for(uint64_t bit_mask=0; bit_mask<=r_max; bit_mask++){
                    test_range_iter(static_cast<int64_t>(r_min), r_max, bit_len, 0, bit_mask, false);
                    uint64_t max_sample_size = r_max + r_min + 10;
                    for(uint64_t sample_size=2; sample_size< max_sample_size; ++sample_size){
                        test_range_iter_2(static_cast<int64_t>(r_min), r_max, bit_len, 0, bit_mask, sample_size, false);
                    }
                }
            }
        }
    }
    else{
        if(bit_len < 2) {
            std::cout << "... ... skip: at least 2 bits for signed necessary" << std::endl;
            return;
        }
        int64_t range_min_s = -static_cast<int64_t>(std::pow(2, bit_len-1)-1);
        int64_t range_max_s = static_cast<int64_t>(std::pow(2, bit_len-1)-1)-1;
        for(int64_t r_min=range_min_s; r_min <= range_max_s; r_min++){
            int64_t r_max_min = std::max(static_cast<int64_t>(0), r_min);
            if(skip_intermediate) r_max_min = range_max_s;
            for(int64_t r_max=r_max_min; r_max <= range_max_s; r_max++){
                for(uint64_t bit_mask=0; bit_mask<=r_max; bit_mask++){
                    test_range_iter(r_min, static_cast<uint64_t>(r_max), bit_len, 1, bit_mask, false);
                    uint64_t max_sample_size = r_max + std::abs(r_min) + 10;
                    for(uint64_t sample_size=2; sample_size< max_sample_size; ++sample_size){
                        test_range_iter_2(r_min, static_cast<uint64_t>(r_max), bit_len, 1, bit_mask, sample_size, false);
                    }
                }
            }
        }
    }
}

void test_range_iter_fringes(uint8_t bit_len, bool signed_){
    std::cout << "test_range_iter_3(bit_len == " << static_cast<int>(bit_len) << ", signed=" << signed_ << ")" << std::endl;
    if(!signed_){
        uint64_t range_max_u = static_cast<uint64_t>((((1UL << (bit_len-1))-1)<<1)+1);

        uint64_t r_max = range_max_u;
        std::vector<uint64_t> bit_masks = { 0, r_max/4, r_max/2, 3*r_max/4, r_max };
        std::vector<uint64_t> sample_sizes = {2, 5, 11, 32, 33, 60};
        for(uint64_t bit_mask : bit_masks){
            for(uint64_t sample_size : sample_sizes){
                test_range_iter_2(static_cast<int64_t>(0), r_max, bit_len, 0, bit_mask, sample_size, false);
            }
        }

        range_max_u = static_cast<uint64_t>((1UL << (static_cast<uint64_t>(bit_len)-1UL))-1UL);
        r_max = range_max_u;
        bit_masks = { 0, r_max/4, r_max/2, 3*r_max/4, r_max };
        sample_sizes = {2, 5, 11, 32, 33, 60};
        for(uint64_t bit_mask : bit_masks){
            for(uint64_t sample_size : sample_sizes){
                test_range_iter_2(static_cast<int64_t>(0), r_max, bit_len, 0, bit_mask, sample_size, false);
            }
        }
    }
    else{
        if(bit_len < 2) {
            std::cout << "... ... skip: at least 2 bits for signed necessary" << std::endl;
            return;
        }
        int64_t range_min_s = -static_cast<int64_t>(std::pow(2, bit_len-1)-1);
        int64_t range_max_s = static_cast<int64_t>(std::pow(2, bit_len-1)-1)-1L;
        
        int64_t r_min=range_min_s;
        int64_t r_max=range_max_s;
        std::vector<uint64_t> bit_masks = { 0, static_cast<uint64_t>(r_max)/4, static_cast<uint64_t>(r_max)/2, 3*static_cast<uint64_t>(r_max)/4, static_cast<uint64_t>(r_max) };
        std::vector<uint64_t> sample_sizes = {2, 5, 11, 32, 33, 60};
        for(uint64_t bit_mask : bit_masks){
            for(uint64_t sample_size : sample_sizes){
                test_range_iter_2(r_min, static_cast<uint64_t>(r_max), bit_len, 1, bit_mask, sample_size, false);
            }
        }
    }
}

void test_range_iter_endings(uint8_t bit_len, bool signed_){
    std::cout << "test_range_iter_3(bit_len == " << static_cast<int>(bit_len) << ", signed=" << signed_ << ")" << std::endl;
    std::vector<uint64_t> sample_sizes = {2, 5, 11, 32, 33, 60};
    if(!signed_){
        uint64_t range_max_u = static_cast<uint64_t>((((1UL << (bit_len-1))-1)<<1)+1);
        uint64_t r_max = range_max_u;
        std::vector<uint64_t> bit_masks = { 0, r_max/4, r_max/2, 3*r_max/4, r_max };
        
        for(uint64_t bit_mask : bit_masks){
            test_range_iter(static_cast<int64_t>(r_max-5), r_max, bit_len, 0, bit_mask, false, true);
            for(uint64_t sample_size : sample_sizes){
                test_range_iter_2(static_cast<int64_t>(r_max-5), r_max, bit_len, 0, bit_mask, sample_size, false);
            }
        }
    }
    else{
        std::cout << "skip signed" << std::endl;
        // if(bit_len < 2) {
        //     std::cout << "... ... skip: at least 2 bits for signed necessary" << std::endl;
        //     return;
        // }
        // int64_t range_min_s = -static_cast<int64_t>(std::pow(2, bit_len-1)-1);
        // int64_t range_max_s = static_cast<int64_t>(std::pow(2, bit_len-1)-1)-1;
        
        // int64_t r_min=range_min_s;
        // int64_t r_max=range_max_s;
        // std::vector<uint64_t> bit_masks = { 0, static_cast<uint64_t>(r_max)/4, static_cast<uint64_t>(r_max)/2, 3*static_cast<uint64_t>(r_max)/4, static_cast<uint64_t>(r_max) };
        
        // for(uint64_t bit_mask : bit_masks){
        //     test_range_iter(r_min, static_cast<uint64_t>, bit_len, 0, bit_mask, false);
        //     for(uint64_t sample_size : sample_sizes){
        //         test_range_iter_2(static_cast<int64_t>(r_max - sample_size), r_max, bit_len, 0, bit_mask, sample_size, false);
        //         test_range_iter_2(static_cast<int64_t>(r_max - 5), r_max, bit_len, 0, bit_mask, sample_size, false);
        //         test_range_iter_2(static_cast<int64_t>(r_max - 10*sample_size), r_max, bit_len, 0, bit_mask, sample_size, false);
        //     }
        // }
    }
}

void test_range_iter_4(uint8_t from_bit_len, uint8_t to_bit_len, bool signed_){
    if(!signed_){
        for(uint8_t bit_len = from_bit_len; bit_len <= to_bit_len; ++bit_len){
            test_range_iter_3(bit_len, false);
        }
    }
    else{
        for(uint8_t bit_len = from_bit_len; bit_len <= to_bit_len; ++bit_len){
            test_range_iter_3(bit_len, true);
        }
    }
}

void from_int_bitlen_tests(int min_bl) {
    std::cout << "from_int: " << std::flush;
    auto b0 = SASS::SASS_Bits::from_int(0, min_bl, -1);
    assert(b0.bit_len() == (min_bl == 0 ? 1 : min_bl));
    b0 = SASS::SASS_Bits::from_int(0, min_bl, 0);
    assert(b0.bit_len() == (min_bl == 0 ? 1 : min_bl));
    b0 = SASS::SASS_Bits::from_int(0, min_bl, 1);
    assert(b0.bit_len() == (min_bl == 0 ? 2 : min_bl));

    auto bm = SASS::SASS_Bits::from_int(-1, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 2 : min_bl));
    bm = SASS::SASS_Bits::from_int(-2, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 2 : min_bl));
    bm = SASS::SASS_Bits::from_int(-3, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 3 : min_bl));
    bm = SASS::SASS_Bits::from_int(-4, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 3 : min_bl));
    bm = SASS::SASS_Bits::from_int(-5, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bm = SASS::SASS_Bits::from_int(-6, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bm = SASS::SASS_Bits::from_int(-7, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bm = SASS::SASS_Bits::from_int(-8, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bm = SASS::SASS_Bits::from_int(-9, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bm = SASS::SASS_Bits::from_int(-10, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bm = SASS::SASS_Bits::from_int(-11, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bm = SASS::SASS_Bits::from_int(-12, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bm = SASS::SASS_Bits::from_int(-13, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bm = SASS::SASS_Bits::from_int(-14, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bm = SASS::SASS_Bits::from_int(-15, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bm = SASS::SASS_Bits::from_int(-16, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bm = SASS::SASS_Bits::from_int(-17, min_bl, -1);
    assert(bm.bit_len() == (min_bl == 0 ? 6 : min_bl));

    auto bp = SASS::SASS_Bits::from_int(1, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 1 : min_bl));
    bp = SASS::SASS_Bits::from_int(2, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 2 : min_bl));
    bp = SASS::SASS_Bits::from_int(3, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 2 : min_bl));
    bp = SASS::SASS_Bits::from_int(4, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 3 : min_bl));
    bp = SASS::SASS_Bits::from_int(5, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 3 : min_bl));
    bp = SASS::SASS_Bits::from_int(6, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 3 : min_bl));
    bp = SASS::SASS_Bits::from_int(7, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 3 : min_bl));
    bp = SASS::SASS_Bits::from_int(8, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bp = SASS::SASS_Bits::from_int(9, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bp = SASS::SASS_Bits::from_int(10, min_bl, -1);
    assert(bp.bit_len() == (min_bl == 0 ? 4 : min_bl));

    bp = SASS::SASS_Bits::from_int(1, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 2 : min_bl));
    bp = SASS::SASS_Bits::from_int(2, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 3 : min_bl));
    bp = SASS::SASS_Bits::from_int(3, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 3 : min_bl));
    bp = SASS::SASS_Bits::from_int(4, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bp = SASS::SASS_Bits::from_int(5, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bp = SASS::SASS_Bits::from_int(6, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bp = SASS::SASS_Bits::from_int(7, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 4 : min_bl));
    bp = SASS::SASS_Bits::from_int(8, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bp = SASS::SASS_Bits::from_int(9, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 5 : min_bl));
    bp = SASS::SASS_Bits::from_int(10, min_bl, 1);
    assert(bp.bit_len() == (min_bl == 0 ? 5 : min_bl));
}

void from_int_tests(){
    SASS::SASS_Bits v = SASS::SASS_Bits::from_int(0);
    assert(v.bit_len() == 1);
    assert(v.__hash__() == 0);
    assert(v.signed_() == false);
    assert(SASS::SASS_Bits::__int__(v) == 0);
    
    v = SASS::SASS_Bits::from_int(1);
    assert(v.bit_len() == 1);
    assert(v.__hash__() == 1);
    assert(v.signed_()== false);
    assert(SASS::SASS_Bits::__int__(v) == 1);
    
    v = SASS::SASS_Bits::from_int(-1);
    assert(v.bit_len() == 2);
    assert(v.__hash__() == static_cast<uint64_t>(-1L));
    assert(v.signed_()== true);
    assert(SASS::SASS_Bits::__int__(v) == -1);
    
    v = SASS::SASS_Bits::from_int(1, 8, 1);
    assert(v.bit_len() == 8);
    assert(v.__hash__() == 1);
    assert(v.signed_()== true);
    assert(SASS::SASS_Bits::__int__(v) == 1);
    
    v = SASS::SASS_Bits::from_int(1, 8, 0);
    assert(v.bit_len() == 8);
    assert(v.__hash__() == 1);
    assert(v.signed_()== false);
    assert(SASS::SASS_Bits::__int__(v) == 1);
    
    v = SASS::SASS_Bits::from_int(1, 0, 1);
    assert(v.bit_len() == 2);
    assert(v.__hash__() == 1);
    assert(v.signed_()== true);
    assert(SASS::SASS_Bits::__int__(v) == 1);
    
    v = SASS::SASS_Bits::from_int(1, 0, 0);
    assert(v.bit_len() == 1);
    assert(v.__hash__() == 1);
    assert(v.signed_()== false);
    assert(SASS::SASS_Bits::__int__(v) == 1);
    
    v = SASS::SASS_Bits::from_int(-1, 0, 1);
    assert(v.bit_len() == 2);
    assert(v.__hash__() == static_cast<uint64_t>(-1L));
    assert(v.signed_()== true);
    assert(SASS::SASS_Bits::__int__(v) == -1);

    for(int i=1; i<=100; ++i){
        v = SASS::SASS_Bits::from_int(i);
        assert(v.__hash__() == i);
        assert(v.signed_()== false);
        assert(SASS::SASS_Bits::__int__(v) == i);

        v = SASS::SASS_Bits::from_int(-i);
        assert(v.__hash__() == static_cast<uint64_t>(-i));
        assert(v.signed_()== true);
        assert(SASS::SASS_Bits::__int__(v) == -i);

        v = SASS::SASS_Bits::from_int(i, 10);
        assert(v.__hash__() == i);
        assert(v.signed_()== false);
        assert(SASS::SASS_Bits::__int__(v) == i);

        v = SASS::SASS_Bits::from_int(-i, 10);
        assert(v.__hash__() == static_cast<uint64_t>(-i));
        assert(v.signed_()== true);
        assert(SASS::SASS_Bits::__int__(v) == -i);

        v = SASS::SASS_Bits::from_int(-i, 10, 1);
        assert(v.__hash__() == static_cast<uint64_t>(-i));
        assert(v.signed_()== true);
        assert(SASS::SASS_Bits::__int__(v) == -i);

        v = SASS::SASS_Bits::from_int(-i, 0, 1);
        assert(v.__hash__() == static_cast<uint64_t>(-i));
        assert(v.signed_()== true);
        assert(SASS::SASS_Bits::__int__(v) == -i);

        v = SASS::SASS_Bits::from_int(i, 0, 1);
        assert(v.__hash__() == i);
        assert(v.signed_()== true);
        assert(SASS::SASS_Bits::__int__(v) == i);
    }

    bool has_ex = false;
    try {
        v = SASS::SASS_Bits::from_int(1, 1, 1);
    } catch(...){ has_ex = true; }
    assert(has_ex);

    has_ex = false;
    try {
        v = SASS::SASS_Bits::from_int(1, 1, 2);
    } catch(...){ has_ex = true; }
    assert(has_ex);

    has_ex = false;
    try {
        v = SASS::SASS_Bits::from_int(-1, 0, 0);
    } catch(...){ has_ex = true; }
    assert(has_ex);

    // v = SASS::SASS_Bits::from_int(1, 8, 0).to_signed();
    // assert(v.bit_len() == 9);
    // assert(v.signed_()== true);
    // assert(SASS::SASS_Bits::__int__(v) == 1);
    // v = SASS::SASS_Bits::from_int(1, 8, 1).to_unsigned();
    // assert(v.bit_len() == 7);
    // assert(v.signed_()== false);
    // assert(SASS::SASS_Bits::__int__(v) == 1);
    std::cout << "ok" << std::endl;
}

void cast_tests(){
    std::cout << "cast: " << std::flush;
    SASS::SASS_Bits tt0 = SASS::SASS_Bits::from_int(8, 8);
    SASS::SASS_Bits tt1 = SASS::SASS_Bits::cast(tt0, 16);
    assert(SASS::SASS_Bits::__int__(tt0) == SASS::SASS_Bits::__int__(tt1));
    assert(SASS::SASS_Bits::__int__(tt0) == 8);
    assert(tt1.bit_len() == 16);

    tt0 = SASS::SASS_Bits::from_int(8, 8, 1);
    tt1 = SASS::SASS_Bits::cast(tt0, 16);
    assert(SASS::SASS_Bits::__int__(tt0) == SASS::SASS_Bits::__int__(tt1));
    assert(SASS::SASS_Bits::__int__(tt0) == 8);
    assert(tt1.bit_len() == 16);

    tt0 = SASS::SASS_Bits::from_int(-8, 8);
    tt1 = SASS::SASS_Bits::cast(tt0, 16);
    assert(SASS::SASS_Bits::__int__(tt0) == SASS::SASS_Bits::__int__(tt1));
    assert(SASS::SASS_Bits::__int__(tt0) == -8);
    assert(tt1.bit_len() == 16);

    tt0 = SASS::SASS_Bits::from_int(7, 8, 1);
    tt1 = SASS::SASS_Bits::cast(tt0, 4);
    assert(SASS::SASS_Bits::__int__(tt0) == SASS::SASS_Bits::__int__(tt1));
    assert(SASS::SASS_Bits::__int__(tt0) == 7);
    assert(tt1.bit_len() == 4);
    
    tt0 = SASS::SASS_Bits::from_int(-7, 8, 1);
    tt1 = SASS::SASS_Bits::cast(tt0, 4);
    assert(SASS::SASS_Bits::__int__(tt0) == SASS::SASS_Bits::__int__(tt1));
    assert(SASS::SASS_Bits::__int__(tt0) == -7);
    assert(tt1.bit_len() == 4);

    tt0 = SASS::SASS_Bits::from_int(15, 8, 1);
    tt1 = SASS::SASS_Bits::cast(tt0, 4);
    assert(7 == SASS::SASS_Bits::__int__(tt1));
    assert(SASS::SASS_Bits::__int__(tt0) == 15);
    assert(tt1.bit_len() == 4);

    tt0 = SASS::SASS_Bits::from_int(15, 8, 0);
    tt1 = SASS::SASS_Bits::cast(tt0, 4);
    assert(15 == SASS::SASS_Bits::__int__(tt1));
    assert(SASS::SASS_Bits::__int__(tt0) == 15);
    assert(tt1.bit_len() == 4);

    tt0 = SASS::SASS_Bits::from_int(-15, 8, 1);
    tt1 = SASS::SASS_Bits::cast(tt0, 4);
    assert(-7 == SASS::SASS_Bits::__int__(tt1));
    assert(SASS::SASS_Bits::__int__(tt0) == -15);
    assert(tt1.bit_len() == 4);

    std::cout << "ok" << std::endl;
}

void operations_test() {
    std::cout << "operations: " << std::flush;
    SASS::SASS_Bits tt0 = SASS::SASS_Bits::from_int(0, 8);
    SASS::SASS_Bits tt0s = SASS::SASS_Bits::from_int(0, 8, 1);
    SASS::SASS_Bits tt1 = SASS::SASS_Bits::from_int(1, 8);
    SASS::SASS_Bits tt1s = SASS::SASS_Bits::from_int(1, 8, 1);
    SASS::SASS_Bits tt7 = SASS::SASS_Bits::from_int(7, 8);
    SASS::SASS_Bits tt5 = SASS::SASS_Bits::from_int(5, 8);
    SASS::SASS_Bits tt5s = SASS::SASS_Bits::from_int(5, 8, 1);
    SASS::SASS_Bits tt8 = SASS::SASS_Bits::from_int(8, 8);
    SASS::SASS_Bits tt4 = SASS::SASS_Bits::from_int(4, 8);
    SASS::SASS_Bits tt4s = SASS::SASS_Bits::from_int(4, 8, 1);
    SASS::SASS_Bits ttm4 = SASS::SASS_Bits::from_int(-4, 8);

    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__add__i(tt0, 1)) == 1);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__add__i(tt0s, -1)) == -1);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__add__b(tt0, true)) == 1);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__add__sb(tt0, tt5)) == 5);

    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mul__i(tt8, 1)) == 8);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mul__i(tt5s, -1)) == -5);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mul__b(tt7, true)) == 7);

    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__matmul__i(tt4, 1)) == 4);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__matmul__i(ttm4, -1)) == 4);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__matmul__b(tt7, true)) == 7);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__matmul__sb(tt4, tt5)) == 20);

    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__floordiv__i(tt5, 2)) == 2);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__floordiv__i(ttm4, 3)) == -1);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__floordiv__i(ttm4, -3)) == 1);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__floordiv__b(tt7, true)) == 7);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__floordiv__sb(tt4, tt5)) == 0);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__floordiv__sb(tt5, tt4)) == 1);

    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mod__i(tt5, 2)) == 1);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mod__i(tt4, 3)) == 1);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mod__i(ttm4, 3)) == 2);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mod__i(tt4s, -3)) == -2);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mod__i(ttm4, -3)) == -1);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mod__b(tt7, true)) == 0);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mod__sb(tt4, tt5)) == 4);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__mod__sb(tt5, tt4)) == 1);

    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__and__(tt0, tt7)) == 0);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__and__(tt5, tt7)) == 5);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__or__(tt5, tt7)) == 7);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__xor__(tt5, tt7)) == 2);

    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__neg__(tt4)) == -4);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__neg__(ttm4)) == 4);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__pos__(ttm4)) == -4);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__pos__(tt4)) == 4);

    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__abs__(tt4)) == 4);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__abs__(ttm4)) == 4);

    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__rshift__(tt4, 1)) == 2);
    assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__lshift__(tt4, 1)) == 8);

    assert(SASS::SASS_Bits::__lt__i(tt4, 0) == false);
    assert(SASS::SASS_Bits::__le__i(tt4, 4) == true);
    assert(SASS::SASS_Bits::__gt__i(tt4, 0) == true);
    assert(SASS::SASS_Bits::__ge__i(tt4, 4) == true);
    assert(SASS::SASS_Bits::__lt__i(tt4s, 0) == false);
    assert(SASS::SASS_Bits::__le__i(tt4s, 4) == true);
    assert(SASS::SASS_Bits::__gt__i(tt4s, 0) == true);
    assert(SASS::SASS_Bits::__ge__i(tt4s, 4) == true);
    assert(SASS::SASS_Bits::__lt__b(tt0, false) == false);
    assert(SASS::SASS_Bits::__lt__b(tt0, true) == true);
    assert(SASS::SASS_Bits::__le__b(tt1, true) == true);
    assert(SASS::SASS_Bits::__le__b(tt1, false) == false);
    assert(SASS::SASS_Bits::__gt__b(tt1, false) == true);
    assert(SASS::SASS_Bits::__gt__b(tt1, true) == false);
    assert(SASS::SASS_Bits::__gt__b(tt0, true) == false);
    assert(SASS::SASS_Bits::__ge__b(tt1, true) == true);
    assert(SASS::SASS_Bits::__lt__sb(tt4, tt5) == true);
    assert(SASS::SASS_Bits::__le__sb(tt4, tt5) == true);
    assert(SASS::SASS_Bits::__le__sb(tt5, tt4) == false);
    assert(SASS::SASS_Bits::__gt__sb(tt4, tt5) == false);
    assert(SASS::SASS_Bits::__gt__sb(tt5, tt4) == true);
    assert(SASS::SASS_Bits::__ge__sb(tt5, tt4) == true);
    assert(SASS::SASS_Bits::__ge__sb(tt4, tt5) == false);

    assert(SASS::SASS_Bits::__lt__b(tt0s, false) == false);
    assert(SASS::SASS_Bits::__lt__b(tt0s, true) == true);
    assert(SASS::SASS_Bits::__le__b(tt1s, true) == true);
    assert(SASS::SASS_Bits::__le__b(tt1s, false) == false);
    assert(SASS::SASS_Bits::__gt__b(tt1s, false) == true);
    assert(SASS::SASS_Bits::__gt__b(tt1s, true) == false);
    assert(SASS::SASS_Bits::__gt__b(tt0s, true) == false);
    assert(SASS::SASS_Bits::__ge__b(tt1s, true) == true);

    std::cout << "ok" << std::endl;
}

void sign_ops_test(){
    std::cout << "signs: " << std::flush;
    SASS::SASS_Bits v = SASS::SASS_Bits::to_signed(SASS::SASS_Bits::from_int(1, 8, 0));
    assert(v.bit_len() == 9);
    assert(v.signed_() == true);
    assert(SASS::SASS_Bits::__int__(v) == 1);
    
    v = SASS::SASS_Bits::to_unsigned(SASS::SASS_Bits::from_int(1, 8, 1));
    assert(v.bit_len() == 7);
    assert(v.signed_() == false);
    assert(SASS::SASS_Bits::__int__(v) == 1);

    v = SASS::SASS_Bits::as_signed(SASS::SASS_Bits::from_int(1, 8, 0));
    assert(v.bit_len() == 8);
    assert(v.signed_() == true);
    assert(SASS::SASS_Bits::__int__(v) == 1);

    v = SASS::SASS_Bits::as_unsigned(SASS::SASS_Bits::from_int(1, 8, 1));
    assert(v.bit_len() == 8);
    assert(v.signed_() == false);
    assert(SASS::SASS_Bits::__int__(v) == 1);
    std::cout << "ok" << std::endl;
}

void assemble_test(){
    auto ff = std::ifstream("__auto_generated_sass_bits_test_gen.txt", std::ios_base::in);
    std::string line;
    int l_counter = 0;
    int sm_counter = 0;
    int sm_enc_width = 0;
    std::vector<std::pair<int, std::vector<IntVector>>> enc_inds;
    std::vector<IntVector> cur;
    int both = 0;
    while(std::getline(ff, line)){
        if(line.starts_with('(')){
            std::string ll = line.substr(1, line.size()-2);
            IntVector v;
            std::string val = "";
            for(const auto& c : ll){
                if(c==','){
                    v.push_back(std::stoi(val));
                    val = "";
                    continue;
                }
                val += c;
            }
            cur.push_back(v);
        }
        else{
            if(both == 2 && cur.size() > 0){
                std::pair<int, std::vector<IntVector>> p = {sm_enc_width, cur};
                enc_inds.push_back(p);
                cur.clear();
                both = 0;
            }
            int v = std::stoi(line);
            if(both==0){
                sm_counter = v;
                both++;
            }
            else{
                sm_enc_width = v;
                both++;
            }
        }
        l_counter++;
    }

    // required test cases:
    // a. bits same size as enc_ind
    int counter = 0;
    int l2_counter = 0;
    for(const std::pair<int, std::vector<IntVector>>& e : enc_inds){
        int enc_width = e.first;
        int enc_counter = 0;
        for(const auto& enc_ind : e.second){
            l2_counter++;
            if(enc_ind.size() == 0){
                enc_counter++;
                continue;
            }
            BitVector instr_bits = BitVector(enc_width, 0);
            
            if(enc_ind.size() > 254) throw std::runtime_error("Unexpected");
            
            uint8_t s = static_cast<uint8_t>(enc_ind.size());
            BitVector vals;
            for(uint8_t i=1; i<=s; ++i){
                vals.push_back(i);
            }
            vals.shrink_to_fit();
            SASS::SASS_Bits b(vals, static_cast<int>(vals.size()), false);

            BitVector new_instr_bits = SASS::SASS_Bits::assemble(b, instr_bits, enc_ind, 0);
            int cc = 0;
            const auto& bits = b.bits();
            int ss = static_cast<int>(new_instr_bits.size());
            for(int i=0; i<ss; ++i){
                if(cc < enc_ind.size() && enc_ind[cc] == i){
                    if(cc > bits.size()) throw std::runtime_error("Unexpected");
                    if(new_instr_bits[i] != bits[cc]) throw std::runtime_error("Unexpected");
                    cc++;
                }
            }
            if(cc != bits.size()) throw std::runtime_error("Unexpected");

            enc_counter++;
        }
        counter++;
    }
}

void scale_multiply_test(){
    std::cout << "scale/multiply: " << std::flush;
    SASS::SASS_Bits tt0 = SASS::SASS_Bits::from_int(8, 8);
    SASS::SASS_Bits tt1 = SASS::SASS_Bits::scale(tt0, 4);
    assert(SASS::SASS_Bits::__int__(tt0)/4 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(8, 8);
    tt1 = SASS::SASS_Bits::scale(tt0, 8);
    assert(SASS::SASS_Bits::__int__(tt0)/8 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(8, 8);
    tt1 = SASS::SASS_Bits::scale(tt0, 16);
    assert(0 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(-8, 8);
    tt1 = SASS::SASS_Bits::scale(tt0, 4);
    assert(SASS::SASS_Bits::__int__(tt0)/4 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(-8, 8);
    tt1 = SASS::SASS_Bits::scale(tt0, 8);
    assert(SASS::SASS_Bits::__int__(tt0)/8 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(-8, 8);
    tt1 = SASS::SASS_Bits::scale(tt0, 16);
    assert(0 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(8);
    tt1 = SASS::SASS_Bits::multiply(tt0, 4);
    assert(0 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(8, 8);
    tt1 = SASS::SASS_Bits::multiply(tt0, 4);
    assert(SASS::SASS_Bits::__int__(tt0)*4 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(-8, 8);
    SASS::SASS_Bits tt2 = SASS::SASS_Bits::__abs__(tt0);
    tt1 = SASS::SASS_Bits::multiply(tt0, 4);
    assert(SASS::SASS_Bits::__int__(tt0)*4 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(8, 8);
    tt1 = SASS::SASS_Bits::multiply(tt0, 4);
    assert(SASS::SASS_Bits::__int__(tt0)*4 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(9, 8);
    tt1 = SASS::SASS_Bits::multiply(tt0, 32);
    assert(32 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(-9, 8);
    tt1 = SASS::SASS_Bits::multiply(tt0, 32);
    assert(-32 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());

    tt0 = SASS::SASS_Bits::from_int(-8, 8);
    tt1 = SASS::SASS_Bits::multiply(tt0, 4);
    assert(SASS::SASS_Bits::__int__(tt0)*4 == SASS::SASS_Bits::__int__(tt1));
    assert(tt0.bit_len() == tt1.bit_len());
    std::cout << "ok" << std::endl;
}

void sass_bit_ranges_test(std::vector<int> bit_len){
    std::cout << "ranges:" << std::endl;
    std::vector<float> perc = {0.10f, 0.20f, 0.30f, 0.40f, 0.50f, 0.60f, 0.70f, 0.80f, 0.90f, 1.0f, 1.1f};
    std::cout << "bits|" << " unsigned " << "|" << " |" << "  signed  " << "|" << std::endl;
    for(const auto& bl : bit_len){
        std::cout << " " << std::setfill('0') << std::setw(2) << bl << ": " << std::flush;
        int64_t mm = static_cast<int64_t>(std::pow(2, bl));
        int p_ind = 0;

        for(int64_t r=0; r<mm; ++r){
            SASS::SASS_Bits_Lib::BitPair b = SASS::SASS_Bits_Lib::val_to_bit_vector(r, 0, 0);
            assert(b.is_signed == false);
            SASS::SASS_Bits s = SASS::SASS_Bits(b.bv, b.bit_len, b.is_signed);

            assert(SASS::SASS_Bits::__int__(s) == r);
            assert(SASS::SASS_Bits::as_unsigned(s) == s);
            if(s.bit_len() > 1){
                uint64_t ll = static_cast<uint64_t>(std::pow(2, b.bit_len-1));
                int64_t rvv = r;
                if(r & ll) 
                    rvv = rvv - (1UL << (b.bit_len));
                SASS::SASS_Bits ss = SASS::SASS_Bits::as_signed(s);
                SASS::SASS_Bits nn = SASS::SASS_Bits::__neg__(ss);
                auto iss = SASS::SASS_Bits::__int__(ss);
                auto inn = SASS::SASS_Bits::__int__(nn);
                assert(iss == rvv);
                assert(inn == -rvv);
            }
            assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__abs__(s)) == std::abs(r));

            while(r >= perc[p_ind]*(mm-1)){
                p_ind++;
                std::cout << "=" << std::flush;
            }
        }
        std::cout << "   " << std::flush;

        mm = static_cast<int64_t>(std::pow(2, bl-1));
        int64_t mmt = 2*mm;
        int64_t cc = 1;
        p_ind = 0;

        for(int64_t r=-mm+1; r<mm; ++r){
            SASS::SASS_Bits_Lib::BitPair b = SASS::SASS_Bits_Lib::val_to_bit_vector(r, 0, 1);
            assert(b.is_signed == true);
            SASS::SASS_Bits s = SASS::SASS_Bits(b.bv, b.bit_len, b.is_signed);

            assert(SASS::SASS_Bits::__int__(s) == r);
            assert(SASS::SASS_Bits::as_signed(s) == s);
            if(r >= 0){
                assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::as_unsigned(s)) == r);
                assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__neg__(s)) == -r);
            }
            assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__abs__(s)) == std::abs(r));
            if(r <= 0){
                assert(SASS::SASS_Bits::__int__(SASS::SASS_Bits::__neg__(s)) == std::abs(r));
            }

            while(cc >= perc[p_ind]*(mmt-1)){
                p_ind++;
                std::cout << "=" << std::flush;
            }
            cc++;
        }

        std::cout << "  ok" << std::endl;
    }
}

void test_next_best_u(uint8_t bit_min, uint8_t bit_max){
    // uint64_t n1;
    uint64_t n2;
    uint64_t n1;
    uint64_t i;
    bool success;
    n2 = SASS::SASS_Range_Lib::next_best_test_u(53, 100, 4, success, i);
    n1 = SASS::SASS_Range_Lib::previous_best_test_u(53, 0, 4, success, i);
    if(n2 != 56) throw std::runtime_error("Unexpected");
    if(n1 != 51) throw std::runtime_error("Unexpected");
    n2 = SASS::SASS_Range_Lib::next_best_test_u(2, 100, 3, success, i);
    n1 = SASS::SASS_Range_Lib::previous_best_test_u(2, 0, 3, success, i);
    if(n2 != 4) throw std::runtime_error("Unexpected");
    if(n1 != 0) throw std::runtime_error("Unexpected");
    n2 = SASS::SASS_Range_Lib::next_best_test_u(3, 100, 3, success, i);
    n1 = SASS::SASS_Range_Lib::previous_best_test_u(3, 0, 3, success, i);
    if(n2 != 4) throw std::runtime_error("Unexpected");
    if(n1 != 0) throw std::runtime_error("Unexpected");
    n2 = SASS::SASS_Range_Lib::next_best_test_u(4, 100, 3, success, i);
    n1 = SASS::SASS_Range_Lib::previous_best_test_u(4, 0, 3, success, i);
    if(n2 != 4) throw std::runtime_error("Unexpected");
    if(n1 != 4) throw std::runtime_error("Unexpected");
    n2 = SASS::SASS_Range_Lib::next_best_test_u(5, 100, 3, success, i);
    n1 = SASS::SASS_Range_Lib::previous_best_test_u(5, 0, 3, success, i);
    if(n2 != 8) throw std::runtime_error("Unexpected");
    if(n1 != 4) throw std::runtime_error("Unexpected");
    n2 = SASS::SASS_Range_Lib::next_best_test_u(5, 100, 2, success, i);
    n1 = SASS::SASS_Range_Lib::previous_best_test_u(5, 0, 2, success, i);
    if(n2 != 5) throw std::runtime_error("Unexpected");
    if(n2 != 5) throw std::runtime_error("Unexpected");
    n2 = SASS::SASS_Range_Lib::next_best_test_u(5, 100, 1, success, i);
    n1 = SASS::SASS_Range_Lib::previous_best_test_u(5, 0, 1, success, i);
    if(n2 != 6) throw std::runtime_error("Unexpected");
    if(n1 != 4) throw std::runtime_error("Unexpected");

    uint64_t max_val_u = static_cast<uint64_t>(std::pow(2, bit_max)-1);
    uint64_t bit_mask_start = (1UL<<bit_min)-1;
    uint64_t bit_mask_max = (1UL<<bit_max)-1;
    for(uint64_t bit_mask = bit_mask_start; bit_mask<=bit_mask_max; ++bit_mask) {
        for(uint64_t min_val = 0; min_val < max_val_u; ++min_val){
            bool success;
            uint64_t res = SASS::SASS_Range_Lib::next_best_test_u(min_val, max_val_u, bit_mask, success, i);
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
}

void test_next_best_s(uint8_t bit_min, uint8_t bit_max){
    int64_t i_s;
    int64_t s2;
    bool success;
    s2 = static_cast<int64_t>(SASS::SASS_Range_Lib::next_best_test_s(-1, 100, 3, success, i_s));
    if(s2 != 0) throw std::runtime_error("Unexpected");
    s2 = static_cast<int64_t>(SASS::SASS_Range_Lib::next_best_test_s(-2, 100, 3, success, i_s));
    if(s2 != 0) throw std::runtime_error("Unexpected");
    s2 = static_cast<int64_t>(SASS::SASS_Range_Lib::next_best_test_s(-3, 100, 3, success, i_s));
    if(s2 != 0) throw std::runtime_error("Unexpected");
    s2 = static_cast<int64_t>(SASS::SASS_Range_Lib::next_best_test_s(-4, 100, 3, success, i_s));
    if(s2 != -4) throw std::runtime_error("Unexpected");
    s2 = static_cast<int64_t>(SASS::SASS_Range_Lib::next_best_test_s(-5, 100, 3, success, i_s));
    if(s2 != -4) throw std::runtime_error("Unexpected");
    s2 = static_cast<int64_t>(SASS::SASS_Range_Lib::next_best_test_s(-6, 100, 3, success, i_s));
    if(s2 != -4) throw std::runtime_error("Unexpected");
    s2 = static_cast<int64_t>(SASS::SASS_Range_Lib::next_best_test_s(-5, 100, 2, success, i_s));
    if(s2 != -4) throw std::runtime_error("Unexpected");
    s2 = static_cast<int64_t>(SASS::SASS_Range_Lib::next_best_test_s(-5, 100, 1, success, i_s));
    if(s2 != -4) throw std::runtime_error("Unexpected");

    int64_t max_val_s = static_cast<uint64_t>(std::pow(2, bit_max-1)-1);
    uint64_t bit_mask_start = (1UL<<bit_min)-1;
    uint64_t bit_mask_max = (1UL<<bit_max)-1;
    for(uint64_t bit_mask = bit_mask_start; bit_mask<=bit_mask_max; ++bit_mask) {
        for(int64_t min_val = -max_val_s; min_val < max_val_s; ++min_val){
            bool success;
            int64_t res = static_cast<int64_t>(SASS::SASS_Range_Lib::next_best_test_s(min_val, max_val_s, bit_mask, success, i_s));
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

void test_next_best(uint8_t bit_min, uint8_t bit_max, bool signed_){
    if(signed_){
        test_next_best_s(bit_min, bit_max);
    }
    else{
        test_next_best_u(bit_min, bit_max);
    }
}

void test_previous_best(uint8_t bit_min, uint8_t bit_max){
    uint64_t n2;
    uint64_t i_u;

    uint64_t min_val_u = static_cast<uint64_t>(std::pow(2, bit_min)-1);
    uint64_t max_val_u = static_cast<uint64_t>(std::pow(2, bit_max)-1);
    uint64_t bit_mask_start = (1UL<<bit_min)-1;
    uint64_t bit_mask_max = (1UL<<bit_max)-1;
    for(uint64_t bit_mask = bit_mask_start; bit_mask<=bit_mask_max; ++bit_mask) {
        for(uint64_t max_val = max_val_u; max_val >= 0; --max_val){
            if(bit_mask == 1 && max_val == 1){
                int x = 4;
            }
            bool success;
            uint64_t res = SASS::SASS_Range_Lib::previous_best_test_u(max_val, min_val_u, bit_mask, success, i_u);
            bool cond1 = (res & bit_mask) == 0;
            bool cond2 = res <= max_val;
            bool cond3 = res >= min_val_u || !success;
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

void test_bit_add(){

}


int main(int argc, char** argv) {

    auto x = SASS::SASS_Bits::from_int(-7084023785355888581, 64, 1);

    uint8_t bit_min = 1;
    uint8_t bit_max = 5;
    bool signed_ = false;
    int test_nr_large = 1000000;
    const int test_nr_small = 100000;
    if(argc == 5){
        std::cout << "Test with bit_len=[" << static_cast<int>(bit_min) << "," << static_cast<int>(bit_max) << "]" << std::endl;
        std::cout << std::endl;

        bit_min = static_cast<uint8_t>(std::stoi(argv[1]));
        bit_max = static_cast<uint8_t>(std::stoi(argv[2]));
        signed_ = static_cast<bool>(std::stoi(argv[3]));
        test_nr_large = static_cast<int>(std::stoi(argv[4]));;
        if(bit_min > bit_max) throw std::runtime_error("Illegal: bit_min > bit_max");
        if(bit_min == 0) throw std::runtime_error("Illegal: bit_min == 0");

        test_next_best(bit_min, bit_max, signed_);
        test_previous_best(bit_min, bit_max);
        test_size_3(bit_min, bit_max, signed_);
        test_range_2(bit_min, bit_max, test_nr_large, signed_);

        return 0;
    }

    auto a = SASS::SASS_Bits::from_int(1,1,0);

    test_next_best_s(1, 9);
    test_next_best_u(1, 9);
    test_previous_best(1, 9);

    from_int_bitlen_tests(0);
    from_int_bitlen_tests(10);
    from_int_tests();
    cast_tests();
    operations_test();
    sign_ops_test();
    assemble_test();
    scale_multiply_test();
    sass_bit_ranges_test({2, 3, 5, 8, 12, 16, 17, 19});

    // Specific ranges
    test_size(SASS::SASS_Range(0, 0, 8, 0, 0), 1);
    test_size(SASS::SASS_Range(1, 0, 8, 0, 0), 256);
    test_size(SASS::SASS_Range(1, 0, 8, 0, 3), 64);
    test_size(SASS::SASS_Range(1, 0, 10, 0, 42), 128);
    test_size(SASS::SASS_Range(1, 0, 8, 1, 0), 256);
    test_size(SASS::SASS_Range(1, 0, 8, 1, 3), 64);
    test_size(SASS::SASS_Range(1, 0, 10, 1, 42), 128);
    test_size(SASS::SASS_Range(4, 8, 4, 0, 3), 2);
    test_size(SASS::SASS_Range(5, 8, 4, 0, 3), 1);
    test_size(SASS::SASS_Range(5, 7, 4, 0, 3), 0);
    test_size(SASS::SASS_Range(5, 11, 5, 0, 3), 1);
    test_size(SASS::SASS_Range(24, 31, 8, 0, 0), 8);
    test_size(SASS::SASS_Range(24, 31, 8, 0, 2), 4);
    test_size(SASS::SASS_Range(8, 128, 8, 0, 3), 31);
    test_size(SASS::SASS_Range(9, 128, 8, 0, 3), 30);
    test_size(SASS::SASS_Range(3, 128, 8, 0, 3), 32);
    test_size(SASS::SASS_Range(-10, 10, 8, 1, 0), 21);
    test_size(SASS::SASS_Range(-10, 10, 8, 1, 3), 5);
    test_size(SASS::SASS_Range(-8, 127, 8, 1, 3), 34);
    test_size(SASS::SASS_Range(2, 10, 8, 0, 3), 2);
    test_size(SASS::SASS_Range(2, 255, 8, 0, 3), 63);
    test_size(SASS::SASS_Range(2, 255, 8, 0, 0), 254);
    test_size(SASS::SASS_Range(5, 11, 5, 0, 4), 4);
    test_size_2(SASS::SASS_Range(-5, 6, 5, 1, 4));
    test_size_2(SASS::SASS_Range(-5, 8, 5, 1, 4));
    test_size_2(SASS::SASS_Range(0, 8, 5, 1, 4));
    test_size_2(SASS::SASS_Range(std::numeric_limits<uint64_t>::max()-10, std::numeric_limits<uint64_t>::max(), 64, 0, 0));
    test_size_2(SASS::SASS_Range(std::numeric_limits<uint64_t>::max()-10, std::numeric_limits<uint64_t>::max(), 64, 0, 4));
    test_size_2(SASS::SASS_Range(std::numeric_limits<uint64_t>::max()-10, std::numeric_limits<uint64_t>::max(), 64, 0, std::numeric_limits<uint64_t>::max()-5));

    test_range(SASS::SASS_Range(1, 0, 8, 0, 0), test_nr_large);
    test_range(SASS::SASS_Range(1, 0, 8, 0, 3), test_nr_large);
    test_range(SASS::SASS_Range(24, 31, 8, 0, 0), test_nr_large);
    test_range(SASS::SASS_Range(24, 31, 8, 0, 1), test_nr_large);
    test_range(SASS::SASS_Range(24, 31, 8, 0, 2), test_nr_large);
    test_range(SASS::SASS_Range(24, 31, 8, 0, 3), test_nr_large);
    test_range(SASS::SASS_Range(2, 255, 8, 0, 3), test_nr_large);
    test_range(SASS::SASS_Range(4, 255, 8, 0, 3), test_nr_large);
    test_range(SASS::SASS_Range(1, 0, 10, 0, 42), test_nr_large);
    test_range(SASS::SASS_Range(1, 0, 8, 1, 0), test_nr_large);
    test_range(SASS::SASS_Range(1, 0, 8, 1, 3), test_nr_large);
    test_range(SASS::SASS_Range(1, 0, 10, 1, 42), test_nr_large);
    test_range(SASS::SASS_Range(24, 31, 8, 0, 2), test_nr_large);
    test_range(SASS::SASS_Range(-4, 4, 8, 1, 2), test_nr_large);
    test_range(SASS::SASS_Range(8, 128, 8, 0, 3), test_nr_large);
    test_range(SASS::SASS_Range(-10, 10, 8, 1, 0), test_nr_large);
    test_range(SASS::SASS_Range(-10, 1, 8, 1, 3), test_nr_large);
    test_range(SASS::SASS_Range(-8, 127, 8, 1, 3), test_nr_large);

    for(uint64_t m=0; m<=31; ++m)
        test_range(SASS::SASS_Range(0, 0, 5, 0, m), test_nr_small);
    for(uint64_t m=0; m<=15; ++m) {
        test_range(SASS::SASS_Range(-16, 15, 5, 1, m), test_nr_small);
        test_range(SASS::SASS_Range(-16, 0, 5, 1, m), test_nr_small);
    }
    
    for(uint64_t m=0; m<=11; ++m) {
        test_range(SASS::SASS_Range(5, 11, 5, 0, m), test_nr_small);
        test_range(SASS::SASS_Range(5, 11, 5, 1, m), test_nr_small);
        test_range(SASS::SASS_Range(-5, 6, 5, 1, m), test_nr_small);
    }

    test_range_iter(1, 0, 3, 0, 0, true);
    test_range_iter(1, 0, 3, 0, 1, true);
    test_range_iter(1, 0, 3, 1, 1, true);
    for(uint64_t bm = 0; bm < 10; bm++){
        test_range_iter(-10, 10, 5, 1, bm, false);
        test_range_iter(0, 20, 5, 0, bm, false);
    }
    for(uint64_t bm = 0; bm < 10; bm++){
        test_range_iter_2(-10, 10, 5, 1, bm, 8, false);
        test_range_iter_2(0, 20, 5, 0, bm, 8, false);
    }

    test_range_iter_4(4, 5, true);
    test_range_iter_4(1, 5, true);
    test_range_iter_4(1, 5, false);

    test_range_iter_fringes(64, true);
    test_range_iter_fringes(64, false);
    test_range_iter_endings(64, false);

    test_range_intersection(0);
    test_range_intersection(1);
    test_range_intersection_2();

    test_range_iter_2(0, (1UL<<16)-1, 17, 1, 3, 32, true);

    SASS::SASS_Range r = SASS::SASS_Range(1, 0, 64, 1, 0);
    std::cout << SASS::SASS_Range::pretty(r) << std::endl;
    SASS::SASS_Range r2 = SASS::SASS_Range(std::numeric_limits<int64_t>::min(), static_cast<uint64_t>(std::numeric_limits<int64_t>::max()), 64, 1, 0);
    std::cout << SASS::SASS_Range::pretty(r2) << std::endl;

    return 0;
}
