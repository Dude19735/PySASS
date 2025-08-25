#pragma once

#include <variant>
#include <string>
#include <sstream>
#include <format>
#include <set>
#include <unordered_map>
#include <map>
#include <bitset>
#include <variant>
#include <type_traits>
#include <utility>
#include <array>

// These are basic types: we don't use Utils in there!!
#include "SASS_Bits.hpp"
#include "SASS_Range.hpp"

namespace SASS {
    using FArgString = std::string;
    using FArgInt = int;
    using FArgSASSBits = SASS_Bits;
    using FArgBool = bool;
    using FArgFloat = float;
    using TConvertVariant = std::variant<FArgInt, FArgFloat, FArgBool, FArgString>;
    using TDomain = std::variant<std::set<SASS_Bits>, SASS_Range>;
    using TOptionsSet = std::set<int>;
    using TStrOptionsSet = std::set<std::string>;
    using TOptionsVec = std::vector<int>;
    using TOptions = std::unordered_map<std::string, TOptionsSet>;

    using FArgs = std::variant<FArgInt, FArgSASSBits, FArgBool>;
    using TEncVals = std::unordered_map<std::string, SASS_Bits>;

    class Utils {
    public:
        static TOptionsSet options_to_set(const TOptions& options, bool filter_invalid=false){
            std::set<int> mm = {};
            for(const auto o : options){
                if(filter_invalid){
                    std::string lower_name = "";
                    std::transform(o.first.begin(), o.first.end(), lower_name.begin(), ::tolower);
                    if(lower_name.starts_with("invalid")) continue;
                }
                for(const auto v : o.second){
                    mm.insert(v);
                }
            }
            return mm;
        }

        static int max_option(const TOptions& options){
            int mm = 0; // we know all values are positive
            for(const auto o : options){
                for(const auto v : o.second){
                    if(v > mm) mm = v;
                }
            }
            return mm;
        }

        static int min_of_set(const std::set<int>& s){
            int mm = std::numeric_limits<int>::max(); // we know all values are positive
            for(const auto v : s){
                if(v < mm) mm = v;
            }
            return mm;
        }

        static uint8_t bit_len(int value) {
            return SASS_Bits_Lib::req_bit_len(static_cast<int64_t>(value), false);
        }

        static std::string strip(const std::string& input, char r = 0) {
            std::set<char> rr;
            if(r == 0) rr = {'\n', ' '};
            else rr = {r};
            std::stringstream res;
            std::string::const_iterator ii = input.begin();
            while(ii != input.end()){
                if(rr.find(*ii) == rr.end()) break;
                ii++;
            }

            std::string::const_reverse_iterator rii = input.rbegin();
            while(rii != input.rend()){
                if(rr.find(*rii) == rr.end()) break;
                rii++;
            }

            return std::string(ii, rii.base());
        }

        static std::vector<std::string> split(const std::string& input, char s = ' ') {
            std::vector<std::string> res = {};
            std::stringstream temp;
            for(const char x : input){
                if(x == s){
                    res.push_back(temp.str());
                    temp.clear();
                    temp.str("");
                    continue;
                }
                temp << x;
            }
            if(!temp.str().empty()) res.push_back(temp.str());
            res.shrink_to_fit();
            return res;
        }

        static std::string replace(const std::string& input, char old_c, char new_c) {
            std::stringstream res;
            std::string::const_iterator from = input.begin();
            std::string::const_iterator to = input.begin();
            while(to != input.end()) {
                if(*to == old_c){
                    if(from != to) res << std::string(from, to);
                    if(new_c != 0) res << new_c;
                    to++;
                    from = to;
                }
                else {
                    to++;
                }
            }
            if(from != to){
                res << std::string(from, to);
            }
            return res.str();
        }

        static TConvertVariant try_convert(float val, bool convert_hex=false, bool convert_bin=false, bool convert_split_bin=false, bool replace_quotes=false){
            return TConvertVariant(val);
        }

        static TConvertVariant try_convert(int val, bool convert_hex=false, bool convert_bin=false, bool convert_split_bin=false, bool replace_quotes=false){
            return TConvertVariant(val);
        }

        static TConvertVariant try_convert(const std::string& val, bool convert_hex=false, bool convert_bin=false, bool convert_split_bin=false, bool replace_quotes=false){
            return TConvertVariant(val.c_str());
        }

        // static TConvertVariant try_convert(const char* val, bool convert_hex=false, bool convert_bin=false, bool convert_split_bin=false, bool replace_quotes=false){
        //     return try_convert(std::string(val), convert_hex, convert_bin, convert_split_bin, replace_quotes);
        // }

        /// @brief 
        /// convert_hex: if True, convert terms like '0xFF' to corresponding integer
        /// convert_bin: if True, convert terms like '0b1001' to corresponding integer
        /// convert_split_bin: if True, convert terms like '0b1_1001_0' to integer corresponding to '0b110010'
        ///
        /// This method is used extremely often.
        /// @param val 
        /// @param convert_hex 
        /// @param convert_bin 
        /// @param convert_split_bin 
        /// @param replace_quotes 
        /// @return 
        static TConvertVariant try_convert(const char* value, bool convert_hex=false, bool convert_bin=false, bool convert_split_bin=false, bool replace_quotes=false){     
            std::string val(value);
            if(replace_quotes) val = Utils::replace(val, '"', 0);
            else val = Utils::strip(val);
            
            // if we have a string => remove the quotes because it will be a string regardless
            val = Utils::strip(val, '"');

            if(val.compare("nan") == 0) return val;
            else if(val.compare("NaN") == 0) return val;
            else if(val.compare("NAN") == 0) return val;

            if(!val.starts_with("0x") && !val.starts_with("0b")){
                if(!val.find(".")){
                    try {
                        return std::stoi(val, nullptr, 10);
                    }
                    catch (const std::invalid_argument& e) {} 
                    catch (const std::out_of_range& e) {}
                }

                try {
                    return std::stof(val);
                }
                catch (const std::invalid_argument& e) {} 
                catch (const std::out_of_range& e) {}
            }

            if(convert_hex && val.starts_with("0x")) {
                try {
                    return std::stoi(val, nullptr, 16);
                }
                catch (const std::invalid_argument& e) {} 
                catch (const std::out_of_range& e) {}
            }

            if(convert_bin && val.starts_with("0b")) {
                if(convert_split_bin)
                    val = Utils::replace(val, '_', 0);

                try {
                    int vv = std::stoi(val, nullptr, 2);
                    // in one instance, we have 0b01_1 things
                    // in this case, just return the string
                    if(val.find('_') != std::string::npos) return val;
                    return vv;
                }
                catch (const std::invalid_argument& e) {} 
                catch (const std::out_of_range& e) {}
            }

            if(val.compare("True") == 0) return true;
            if(val.compare("False") == 0) return false;

            return val;
        }
    };
}