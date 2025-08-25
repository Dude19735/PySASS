#pragma once
#include <stdint.h>
#include <exception>
#include <iostream>
#include <vector>
#include <format>
#include <cmath>
#include <random>
#include <time.h>
#include <bitset>
#include <fstream>
#include <numeric>
#include <memory>
#include <variant>
#include <algorithm>
#include <sstream>
#include <map>
#include <set>
#include <thread>
#include <omp.h>
#include "../external/lz4/lz4.h"
#include <type_traits>
#include "SASS_Bits.hpp"
#include "SASS_Range.hpp"

template<typename TSet, typename TRange>
using TVariant = std::variant<std::set<TSet>, TRange>;
template<typename TSet, typename TRange>
using TVariantMap = std::map<std::string, TVariant<TSet, TRange>>;
template<typename TSet, typename TRange>
using TVariantVector = std::vector<TVariantMap<TSet, TRange>>;

using TVariantBR = TVariant<SASS::SASS_Bits, SASS::SASS_Range>;
using TVariantMapBR = TVariantMap<SASS::SASS_Bits, SASS::SASS_Range>;
using TVariantVectorBR = TVariantVector<SASS::SASS_Bits, SASS::SASS_Range>;
using TAllVariantsBR = std::vector<TVariantVectorBR>;

namespace SASS {
    typedef std::map<std::string, size_t> TDomp;
    typedef std::vector<std::string> TDompNok;

    struct DeserilalizeResult {
        TDomp domp;
        TAllVariantsBR domp_v;
        TDompNok domp_nok;
    };

    struct DeserializeHelper {
        uint8_t* from_ptr;
        uint8_t* to_ptr;
        std::string instr_name;
    };

    struct DeserializeHelperRes {
        std::string instr_name;
        std::vector<TVariantMapBR> t_variant_map;
    };

    constexpr size_t S_INSTR_NAME_SIZE = 64;
    constexpr size_t S_ENC_NAME_SIZE = 63;

    class SASS_Enc_Dom_Lib {
        struct S_Enc_Set {
            uint32_t entry_num; // how many entries in the set
            SASS_Bits_Lib::State* entries; // all entries
        };

        typedef SASS_Range::State S_Enc_Range;

        struct S_Enc_Name {
            char name[S_ENC_NAME_SIZE]; // encoding designation
            uint8_t type; // 0 == S, 1 == R
            uint8_t* data; // either set of SASS_Bit or SASS_Range
        };

        struct S_Instr {
            char instr[S_INSTR_NAME_SIZE]; // instruction name chars
        };

        struct S_Variant {
            uint32_t var_count; // how many variants
            uint32_t var_enc_num; // how many encodings per variant
            uint8_t* variants; // ptr to variant data
        };

        struct S_Nok_Instr {
            uint32_t instr_num;
            char* instr;
        };

        public:
        static void serialize_bin(const std::string& filename, const TDomp& domp, const TAllVariantsBR& domp_v, const TDompNok& domp_nok, bool compress=true){
            size_t total_size_byte = 0;
            size_t sass_range_size = SASS_Range::get_bin_state_size();
            if(sass_range_size != 32) throw std::runtime_error("Unexpected: sass_range_size != 32");

            std::map<std::string, size_t> instr_bitlen;
            std::map<std::string, std::vector<size_t>> instr_variants_byte_size;
            for(const auto& instr_vals : domp) {
                size_t total_size_byte_instr = 0;

                // size check for later, -1 is for \0 termination
                if(instr_vals.first.size() > S_INSTR_NAME_SIZE-1) throw std::runtime_error("Unexpected: instr_vals.first.size() > S_INSTR_NAME_SIZE-1");
                total_size_byte_instr += S_INSTR_NAME_SIZE;
                total_size_byte_instr += sizeof(size_t);
                total_size_byte_instr += sizeof(uint32_t);
                total_size_byte_instr += sizeof(uint32_t);

                const std::vector<TVariantMapBR>& all_variants = domp_v.at(instr_vals.second);
                std::vector<size_t> all_variants_byte_size(all_variants.size());
                size_t variant_counter = 0;
                for(const auto& v : all_variants){
                    size_t variant_byte_size = sizeof(size_t);
                    for(const auto& a_s : v){
                        // size check for later, -1 is for \0 termination
                        if(a_s.first.size() > S_ENC_NAME_SIZE-1) throw std::runtime_error("Unexpected: a_s.first.size() > S_ENC_NAME_SIZE-1");
                        variant_byte_size += (S_ENC_NAME_SIZE + sizeof(uint8_t));
                        if(a_s.second.index() == 0){
                            const std::set<SASS_Bits>& sass_bits_set = std::get<std::set<SASS_Bits>>(a_s.second);
                            variant_byte_size += sizeof(uint32_t);
                            for(const auto& s : sass_bits_set){
                                size_t size = SASS_Bits::get_bin_state_size(s);
                                if(size > 255) throw std::runtime_error("Unexpected: size > 255");
                                variant_byte_size += size;
                            }
                        }
                        else if(a_s.second.index() == 1){
                            const SASS_Range& sass_range = std::get<SASS_Range>(a_s.second);
                            variant_byte_size += sass_range_size;
                        }
                    }
                    total_size_byte_instr += variant_byte_size;
                    all_variants_byte_size.at(variant_counter) = variant_byte_size;
                    variant_counter++;
                }
                instr_bitlen.insert({instr_vals.first, total_size_byte_instr});
                instr_variants_byte_size.insert({instr_vals.first, std::move(all_variants_byte_size)});
                total_size_byte += total_size_byte_instr;
            }

            size_t domp_nok_size = domp_nok.size()*S_INSTR_NAME_SIZE;
            if(domp_nok_size > 0){
                total_size_byte += domp_nok_size + 1;
            }

            total_size_byte += 2*sizeof(uint64_t);
            std::vector<uint8_t> stream(total_size_byte, 0);

            uint8_t* ptr = &stream[0];
            *reinterpret_cast<uint64_t*>(ptr) = total_size_byte;
            ptr+=sizeof(uint64_t);
            *reinterpret_cast<uint64_t*>(ptr) = (domp_nok_size > 0 ? domp_nok_size+1 : 0);
            ptr+=sizeof(uint64_t);
            for(const auto& instr_vals : domp) {
                const std::vector<TVariantMapBR>& all_variants = domp_v.at(instr_vals.second);

                const auto str_size = instr_vals.first.size(); // size constraints checked earlier
                instr_vals.first.copy(reinterpret_cast<char*>(ptr), str_size);
                *(ptr+str_size) = '\0';
                std::string str_res = std::string(reinterpret_cast<char*>(ptr));
                const int cmp_str_res = str_res.compare(instr_vals.first);
                if(cmp_str_res != 0) throw std::runtime_error("Unexpected: cmp_str_res != 0");
                ptr += S_INSTR_NAME_SIZE;
                size_t c_bsize = instr_bitlen.at(instr_vals.first);
                *reinterpret_cast<size_t*>(ptr) = c_bsize;
                ptr += sizeof(size_t);

                uint32_t var_count = static_cast<uint32_t>(all_variants.size());
                uint32_t var_enc_num = static_cast<uint32_t>(all_variants.front().size());
                *reinterpret_cast<uint32_t*>(ptr) = var_count;
                ptr += sizeof(uint32_t);
                *reinterpret_cast<uint32_t*>(ptr) = var_enc_num;
                ptr += sizeof(uint32_t);

                size_t variant_counter = 0;
                const std::vector<size_t>& all_variants_byte_size = instr_variants_byte_size.at(str_res);
                if(all_variants_byte_size.size() != all_variants.size()) throw std::runtime_error("Unexpected: all_variants_byte_size.size() != all_variants.size()");
                for(const auto& v : all_variants){
                    *reinterpret_cast<size_t*>(ptr) = all_variants_byte_size.at(variant_counter);
                    ptr += sizeof(size_t);

                    for(const auto& a_s : v){
                        const auto enc_size = a_s.first.size(); // size constraints checked earlier
                        a_s.first.copy(reinterpret_cast<char*>(ptr), enc_size);
                        *(ptr+enc_size) = '\0';
                        std::string enc_res = std::string(reinterpret_cast<char*>(ptr));
                        const int cmp_enc_res = enc_res.compare(a_s.first);
                        if(cmp_enc_res != 0) throw std::runtime_error("Unexpected: cmp_enc_res != 0");
                        ptr += S_ENC_NAME_SIZE;
                        
                        if(a_s.second.index() == 0){
                            *ptr = 0;
                            ptr++;
                            const std::set<SASS_Bits>& sass_bits_set = std::get<std::set<SASS_Bits>>(a_s.second);
                            *reinterpret_cast<uint32_t*>(ptr) = static_cast<uint32_t>(sass_bits_set.size());
                            ptr+=sizeof(uint32_t);
                            for(const auto& s : sass_bits_set){
                                SASS_Bits_Lib::State state = SASS_Bits::get_bin_state(s);
                                size_t state_size = SASS_Bits::get_bin_state_size(s);
                                *ptr = state.sign;
                                ptr++;
                                *ptr = state.bit_len;
                                ptr++;
                                memcpy(ptr, state.bits, state_size-2);
                                ptr+=(state_size-2);

                                SASS_Bits res_bits = SASS_Bits::set_from_bin_state(ptr - state_size);
                                if(res_bits != s) throw std::runtime_error("Unexpected: res_bits != s");
                            }
                        }
                        else if(a_s.second.index() == 1){
                            *ptr = 1;
                            ptr++;
                            const SASS_Range& sass_range = std::get<SASS_Range>(a_s.second);
                            SASS_Range::State state = SASS_Range::get_bin_state(sass_range);
                            size_t state_size = SASS_Range::get_bin_state_size();
                            *reinterpret_cast<int64_t*>(ptr) = state.range_min;
                            ptr+=sizeof(int64_t);
                            *reinterpret_cast<uint64_t*>(ptr) = state.range_max;
                            ptr+=sizeof(uint64_t);
                            *reinterpret_cast<uint64_t*>(ptr) = state.bit_mask;
                            ptr+=sizeof(uint64_t);
                            *ptr = state.bit_len;
                            ptr++;
                            *ptr = state.sign;
                            ptr+=(7*sizeof(uint8_t));

                            const SASS_Range res = SASS_Range::set_from_bin_state(ptr - state_size);
                            if(res != sass_range) throw std::runtime_error("Unexpected: res != sass_range");
                        }
                    }
                    variant_counter++;
                }
                if(variant_counter != all_variants.size()) throw std::runtime_error("Unexpected: variant_counter != all_variants.size()");
            }

            if(domp_nok_size > 0){
                *ptr = '+';
                ptr++;
                for(const auto& nok : domp_nok){
                    const auto str_size = nok.size(); // size constraints checked earlier
                    if(str_size > S_INSTR_NAME_SIZE) throw std::runtime_error("Unexpected: str_size > S_INSTR_NAME_SIZE");
                    nok.copy(reinterpret_cast<char*>(ptr), str_size);
                    *(ptr+str_size) = '\0';
                    std::string nok_res = std::string(reinterpret_cast<char*>(ptr));
                    const int cmp_nok_res = nok_res.compare(nok);
                    if(cmp_nok_res != 0) throw std::runtime_error("Unexpected: cmp_nok_res != 0");
                    ptr += S_INSTR_NAME_SIZE;
                }
            }

            uint64_t expected = reinterpret_cast<uint64_t>(stream.data()) + total_size_byte;
            uint64_t result = reinterpret_cast<uint64_t>(ptr);
            if(result != expected) throw std::runtime_error("Unexpected: result != expected");

            char* data= nullptr;
            size_t data_size = 0;
            std::vector<uint8_t> compressed;
            if(compress){
                const int max_dst_size = LZ4_compressBound(stream.size() - 2*sizeof(size_t));
                // We will use that size for our destination boundary when allocating space.
                compressed.resize(max_dst_size);
                const char* compress_src = reinterpret_cast<const char*>(stream.data()+2*sizeof(size_t));
                size_t src_size = stream.size()-2*sizeof(size_t);
                char* compress_trgt = reinterpret_cast<char*>(compressed.data());
                const int compressed_data_size = LZ4_compress_default(compress_src, compress_trgt, src_size, max_dst_size);
                data = reinterpret_cast<char*>(compressed.data());
                data_size = static_cast<size_t>(compressed_data_size);

                /**
                 * Decoding example for reference
                 */
                // std::vector<uint8_t> test_target(src_size);
                // const int decompressedSize = LZ4_decompress_safe(
                //     reinterpret_cast<const char*>(compressed.data()),
                //     reinterpret_cast<char*>(test_target.data()), 
                //     compressed_data_size,
                //     src_size
                // );

                // Compare compress and decompress
                // std::vector<uint8_t>::const_iterator tt_ii = test_target.cbegin();
                // std::vector<uint8_t>::const_iterator ss_ii = stream.cbegin() + 16;
                // while(tt_ii != test_target.cend()){
                //     if(*tt_ii != *ss_ii) throw std::runtime_error("Unexüp");
                //     tt_ii++;
                //     ss_ii++;
                // }
            }
            else{
                data = reinterpret_cast<char*>(stream.data() + 2*sizeof(size_t));
                data_size = total_size_byte - 2*sizeof(size_t);
            }

            total_size_byte += sizeof(size_t); // include data_size
            size_t real_domp_nok_size = (domp_nok_size > 0 ? domp_nok_size + 1 : 0);
            auto ff = std::ofstream(filename, std::ios_base::out | std::ios_base::binary);
            if(!ff.is_open()) throw std::runtime_error(std::vformat("Unexpected: unable to open file [{0}]", std::make_format_args(filename)));
            ff.write(reinterpret_cast<char*>(&total_size_byte), sizeof(size_t));
            ff.write(reinterpret_cast<char*>(&real_domp_nok_size), sizeof(size_t));
            ff.write(reinterpret_cast<char*>(&data_size), sizeof(size_t));
            ff.write(data, data_size);
            ff.close();
        }

        static DeserilalizeResult deserialize_bin(const std::string& filename, bool compressed, bool show_progress){
            const auto t1 = std::chrono::high_resolution_clock::now();
            if(show_progress) {
                std::cout << "Open" << (compressed ? " [Compressed]" : "") << ": " << filename << "..." << std::flush;
            }
            
            auto ff = std::ifstream(filename, std::ios_base::in | std::ios_base::binary);
            if(!ff.is_open()) throw std::runtime_error(std::vformat("Unexpected: unable to open file [{0}]", std::make_format_args(filename)));

            size_t total_size_byte = 0;
            size_t domp_nok_size = 0;
            size_t data_size = 0;
            ff.read(reinterpret_cast<char*>(&total_size_byte), sizeof(size_t));
            ff.read(reinterpret_cast<char*>(&domp_nok_size), sizeof(size_t));
            ff.read(reinterpret_cast<char*>(&data_size), sizeof(size_t));

            std::vector<uint8_t> stream(total_size_byte-3*sizeof(size_t));
            if(compressed){
                if(data_size + 3*sizeof(size_t) >= total_size_byte) throw std::runtime_error("Illegal: request decompression but input file likely not compressed! [data_size + 3*sizeof(size_t) >= total_size_byte]");
                std::vector<uint8_t> c_stream(data_size);
                ff.read(reinterpret_cast<char*>(c_stream.data()), data_size);
                const int decompressedSize = LZ4_decompress_safe(
                    reinterpret_cast<const char*>(c_stream.data()), 
                    reinterpret_cast<char*>(stream.data()), 
                    data_size,
                    stream.size()
                );
                if(decompressedSize != total_size_byte-3*sizeof(size_t)) throw std::runtime_error("Unexpected: decompressedSize != total_size_byte-3*sizeof(size_t)");
            }
            else {
                if(data_size + 3*sizeof(size_t) != total_size_byte) throw std::runtime_error("Unexpected: data_size + 3*sizeof(size_t) != total_size_byte");
                ff.read(reinterpret_cast<char*>(stream.data()), data_size);
            }
            ff.close();

            const auto t2 = std::chrono::high_resolution_clock::now();
            if(show_progress) {
                const auto diff2 = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
                std::cout << "ok [" << diff2 << "]ms" << std::endl;
            }

            total_size_byte -= 3*sizeof(size_t);
            if(stream.size() != total_size_byte) throw std::runtime_error("Unexpected: stream.size() != total_size_byte");
            
            std::vector<DeserializeHelper> instr;
            uint8_t* ptr = &stream[0];
            DeserilalizeResult res;
            size_t instr_byte_size_total = 0;
            uint8_t* ptr_max = ptr + (total_size_byte - domp_nok_size);
            while(ptr < ptr_max){
                std::string instr_name = std::string(reinterpret_cast<char*>(ptr));
                size_t instr_byte_size = *reinterpret_cast<size_t*>(ptr+S_INSTR_NAME_SIZE);
                instr_byte_size_total += instr_byte_size;
                res.domp.insert({instr_name, {}});
                uint8_t* from_ptr = ptr + S_INSTR_NAME_SIZE + sizeof(size_t);
                uint8_t* to_ptr = ptr + instr_byte_size;
                instr.push_back(DeserializeHelper{.from_ptr=from_ptr,.to_ptr=to_ptr,.instr_name=instr_name});
                ptr += instr_byte_size;
                if(ptr > ptr_max) throw std::runtime_error("Unexpected: ptr > ptr_max [6]");
            }
            instr.shrink_to_fit();

            size_t i_size = instr.size();
            if(show_progress) std::cout << std::vformat("   Loaded 0/{0}...", std::make_format_args(i_size)) << '\r' << std::flush;
            
            omp_set_num_threads(2*std::thread::hardware_concurrency());
            res.domp_v.resize(i_size);
            std::vector<std::pair<std::string, size_t>> domp_inds(i_size);

            size_t counter = 0;
            for(size_t i=0; i<i_size; ++i) {
                const DeserializeHelper& h = instr.at(i);
                res.domp_v[i] = std::move(SASS_Enc_Dom_Lib::deserialize_bin_variant(h.from_ptr, h.to_ptr));
                domp_inds[i] = {h.instr_name, i};

                if(show_progress){
                    counter++;
                    if(counter % 50 == 0) std::cout << "                      " << '\r' << std::vformat("   Loaded {0}/{1}...", std::make_format_args(counter, i_size)) << '\r' << std::flush;
                }
            }

            for(const auto& r : domp_inds){
                res.domp.at(r.first) = r.second;
            }

            if(domp_nok_size > 0){
                ptr_max = ptr + domp_nok_size;

                if(*ptr != '+') throw std::runtime_error("Unexpected: *ptr != '+'");
                ptr++;
                if(ptr > ptr_max) throw std::runtime_error("Unexpected: ptr > ptr_max [5]");

                while(ptr < ptr_max){
                    std::string nok_instr_name = std::string(reinterpret_cast<char*>(ptr));
                    ptr += S_INSTR_NAME_SIZE;
                    res.domp_nok.push_back(nok_instr_name);
                }
            }
            if(ptr != ptr_max) throw std::runtime_error("Unexpected: ptr != ptr_max");
            
            const auto t4 = std::chrono::high_resolution_clock::now();
            if(show_progress){
                const auto diff4 = std::chrono::duration_cast<std::chrono::milliseconds>(t4 - t2).count();
                std::cout << "                      " << '\r' << std::vformat(" = Loaded {0}/{1}...ok [{2}]ms", std::make_format_args(counter, i_size, diff4)) << std::endl;
            }
            return std::move(res);
        }

        static std::vector<TVariantMapBR> deserialize_bin_variant(uint8_t* ptr, uint8_t* ptr_max){
            S_Variant var = *reinterpret_cast<S_Variant*>(ptr);
            uint32_t var_count = var.var_count;
            uint32_t var_enc_num = var.var_enc_num;
            ptr += 2*sizeof(uint32_t);

            std::vector<TVariantMapBR> all_variants(var_count);
            std::vector<uint8_t*> thl_ptrs(var_count);
            std::vector<uint8_t*> thl_ptrs_max(var_count);
            size_t c_offset = 0;
            for(uint32_t var_c=0; var_c < var_count; ++var_c){
                size_t variant_size = *reinterpret_cast<size_t*>(ptr + c_offset);
                thl_ptrs.at(var_c) = ptr + c_offset;
                if(var_c > 0) thl_ptrs_max.at(var_c-1) = thl_ptrs.at(var_c);
                c_offset += variant_size;
            }
            thl_ptrs_max.at(var_count-1) = ptr_max;

            #pragma omp parallel for
            for(uint32_t var_c=0; var_c < var_count; ++var_c){
                TVariantMapBR variant_dict;
                
                uint8_t* thl_ptr = thl_ptrs.at(var_c);
                uint8_t* thl_ptr_max = thl_ptrs_max.at(var_c);

                size_t variant_size = *reinterpret_cast<size_t*>(thl_ptr);
                thl_ptr += sizeof(size_t);
                size_t test_variant_size = sizeof(size_t);

                for(uint32_t var_enc_n=0; var_enc_n<var_enc_num; ++var_enc_n){
                    std::string enc_identifier = std::string(reinterpret_cast<char*>(thl_ptr));
                    thl_ptr += S_ENC_NAME_SIZE;
                    test_variant_size += S_ENC_NAME_SIZE; // test

                    uint8_t type = *thl_ptr;
                    thl_ptr++;
                    test_variant_size++; // test

                    if(thl_ptr > thl_ptr_max) throw std::runtime_error("Unexpected: thl_ptr > thl_ptr_max [0]");
                    if(type == 0){
                        std::set<SASS_Bits> sass_bits_set;
                        S_Enc_Set s = *reinterpret_cast<S_Enc_Set*>(thl_ptr);
                        thl_ptr += sizeof(uint32_t);
                        test_variant_size += sizeof(uint32_t); // test

                        if(thl_ptr > thl_ptr_max) throw std::runtime_error("Unexpected: thl_ptr > thl_ptr_max [1]");
                        for(uint32_t en=0; en<s.entry_num; ++en){
                            SASS_Bits sass_bits = SASS_Bits::set_from_bin_state(thl_ptr);
                            size_t state_size = SASS_Bits::get_bin_state_size(sass_bits);
                            thl_ptr += state_size;
                            test_variant_size += state_size; // test

                            if(thl_ptr > thl_ptr_max) throw std::runtime_error("Unexpected: thl_ptr > thl_ptr_max [2]");
                            sass_bits_set.insert(sass_bits);
                        }
                        variant_dict.insert({enc_identifier, sass_bits_set});
                    }
                    else if(type == 1){
                        SASS_Range sass_range = SASS_Range::set_from_bin_state(thl_ptr);
                        size_t state_size = SASS_Range::get_bin_state_size();
                        thl_ptr += state_size;
                        test_variant_size += state_size; // test

                        if(thl_ptr > thl_ptr_max) throw std::runtime_error("Unexpected: thl_ptr > thl_ptr_max [3]");
                        variant_dict.insert({enc_identifier, sass_range});
                    }
                    else throw std::runtime_error("Unexpected: type not in {0,1}");
                }
                all_variants[var_c] = std::move(variant_dict);
                if(variant_size != test_variant_size) throw std::runtime_error("Unexpected: variant_size != test_variant_size");
            }
            return all_variants;
        }

        static void serialize(const std::string& filename, const TDomp& domp, const TAllVariantsBR& domp_v, const TDompNok& domp_nok){
            const char or_ = '|';
            const char and_ = '&';
            const char is_ = ':';
            const char set_ = 'S';
            const char range_ = 'R';
            const char sep = '\n';
            const char comma = ',';
            const char nok_i = '+';
            
            std::stringstream ss;
            std::vector<std::string> lines;
            size_t instr_ind = 0;
            size_t instr_ind_max = domp.size();
            for(const auto& instr_vals : domp){
                ss.str("");
                ss << instr_vals.first;
                ss << sep;

                const std::vector<TVariantMapBR>& all_variants = domp_v.at(instr_vals.second);

                size_t vals_ind = 0;
                size_t vals_ind_max = all_variants.size();
                for(const auto& v : all_variants){
                    size_t v_ind = 0;
                    size_t v_ind_max = v.size();
                    for(const auto& a_s : v){
                        ss << a_s.first;
                        ss << is_;
                        if(a_s.second.index() == 0){
                            const std::set<SASS_Bits>& sass_bits_set = std::get<std::set<SASS_Bits>>(a_s.second);
                            ss << set_;
                            std::vector<std::string> sets;
                            for(const auto& sv : sass_bits_set){
                                sets.push_back(SASS_Bits::serialize(sv));
                            }
                            std::sort(sets.begin(), sets.end());
                            size_t sv_ind = 0;
                            size_t sv_ind_max = sass_bits_set.size();
                            for(const auto& s : sets){
                                ss << s;
                                if(sv_ind < sv_ind_max - 1) ss << comma;
                                sv_ind++;
                            }
                        }
                        else if(a_s.second.index() == 1){
                            const size_t i = a_s.second.index();
                            const SASS_Range& sass_range = std::get<SASS_Range>(a_s.second);
                            ss << range_;
                            ss << SASS_Range::serialize(sass_range);
                        }
                        else throw std::runtime_error("Unexpected: domain file contains something else than set<SASS_Bits> or SASS_Range");

                        if(v_ind < v_ind_max - 1) ss << and_;
                        v_ind++;
                    }
                    if(vals_ind < vals_ind_max - 1) ss << or_;
                    vals_ind++;
                }
                if(instr_ind < instr_ind_max - 1) ss << sep;
                instr_ind++;
                lines.push_back(ss.str());
            }

            ss.str("");
            size_t nok_ind = 0;
            size_t nok_ind_max = domp_nok.size();
            for(const auto& nok : domp_nok){
                ss << nok;
                if(nok_ind < nok_ind_max-1) ss << comma;
                nok_ind++;
            }
            std::string nok_str = ss.str();
            if(nok_str.size() > 0){
                lines.push_back(std::string(1, sep));
                lines.push_back(std::string(1, nok_i));
                lines.push_back(std::string(1, sep));
                lines.push_back(nok_str);
            }

            auto ff = std::ofstream(filename, std::ios_base::out);
            if(!ff.is_open()) throw std::runtime_error(std::vformat("Unexpected: unable to open file [{0}]", std::make_format_args(filename)));
            for(const auto& line : lines){
                ff << line;
            }
            ff.close();
        }

        static DeserilalizeResult deserialize(const std::string& filename){
            auto ff = std::ifstream(filename, std::ios_base::in);
            if(!ff.is_open()) throw std::runtime_error(std::vformat("Unexpected: unable to open file [{0}]", std::make_format_args(filename)));

            std::string line = "";
            int state = 0;
            std::string instr_name = "";
            std::vector<std::string> lines;
            while(std::getline(ff, line)){
                lines.push_back(line);
            }
            ff.close();

            DeserilalizeResult res;
            size_t instr_counter = 0;
            for(const std::string& line : lines){
                if(state == 0){
                    if(line.starts_with('+')){
                        // nok classes
                        state = 2;
                    }
                    else{
                        // instruction name, for example ATOM
                        instr_name = line;
                        state = 1;
                    }
                }
                else if(state == 1){
                    std::vector<std::string> variants;
                    std::stringstream ss;
                    ss.str("");
                    for(const auto& c : line){
                        if(c == '|' || c == '\n') {
                            variants.push_back(ss.str());
                            ss.str("");
                        }
                        else ss << c;
                    }
                    variants.push_back(ss.str());
                    ss.str("");

                    std::vector<TVariantMapBR> all_variants;
                    for(const auto& v : variants){
                        ss.str("");
                        TVariantMapBR variant_dict;
                        int vstate = 0;
                        std::string::const_iterator ii = v.begin();
                        std::string::const_iterator ii_end = v.end();
                        std::string enc_identifier = "";
                        while(ii != ii_end){
                            if(vstate == 0 && *ii == ':'){
                                // this is the encoding identifier, for example src_rel_sb
                                enc_identifier = ss.str();
                                ss.str("");
                                vstate = 1;
                                ++ii;
                            }
                            else if(vstate == 1){
                                if(*ii == 'S') vstate = 2;
                                else if(*ii == 'R') vstate = 3;
                                else throw std::runtime_error(std::vformat("Unexpected: c={0} but has to be one of S or R", std::make_format_args(*ii)));
                                ++ii;
                            }
                            else if(vstate == 2){
                                // this is a set
                                std::set<SASS_Bits> sass_bits_set;
                                int comma_counter = 0;
                                while(ii != ii_end && *ii != '&'){
                                    if(*ii == ',' || *ii == '\n'){
                                        if(comma_counter < 1){
                                            comma_counter++;
                                            ss << *ii;
                                        }
                                        else if(comma_counter == 1) {
                                            SASS_Bits bits = SASS_Bits::deserialize(ss.str());
                                            sass_bits_set.insert(bits);
                                            comma_counter = 0;
                                            ss.str("");
                                        }
                                    }
                                    else ss << *ii;
                                    ++ii;
                                }
                                SASS_Bits bits = SASS_Bits::deserialize(ss.str());
                                sass_bits_set.insert(bits);
                                ss.str("");

                                variant_dict.insert({enc_identifier, sass_bits_set});
                                vstate = 0;
                                if(ii != ii_end) ++ii;
                            }
                            else if(vstate == 3){
                                // this is a range
                                while(ii != ii_end && *ii != '&'){
                                    ss << *ii;
                                    ++ii;
                                }
                                const std::string vals = ss.str();
                                SASS_Range range = SASS_Range::deserialize(vals);
                                variant_dict.insert({enc_identifier, range});
                                ss.str("");
                                vstate = 0;

                                if(ii != ii_end) ++ii;
                            }
                            else{
                                ss << *ii;
                                ++ii;
                            }
                        }
                        all_variants.push_back(variant_dict);
                    }
                    res.domp_v.push_back(all_variants);
                    res.domp.insert({instr_name, instr_counter});
                    instr_counter++;
                    state = 0;
                }
                else if(state == 2) {
                    std::stringstream ss;
                    for(const auto& c : line){
                        if(c == ',' || c == '\n'){
                            res.domp_nok.push_back(ss.str());
                            ss.str("");
                        }
                        else ss << c;
                    }
                    res.domp_nok.push_back(ss.str());
                }
                else throw std::runtime_error("Unexpected: non defined state");
            }
            return res;
        }
    };
}