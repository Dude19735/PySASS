#include <fstream>
#include <vector>
#include <format>
#include <chrono>

#include "../src/SASS_Enc_Dom.hpp"

void test(const std::string& p_in, const std::string& p_out){
    std::vector<std::string> lines_in;
    std::vector<std::string> lines_out;

    auto ff_in = std::ifstream(p_in, std::ios_base::in);
    if(!ff_in.is_open()) throw std::runtime_error("Unexpected");
    std::string line = "";
    while(std::getline(ff_in, line)) lines_in.push_back(line);
    ff_in.close();

    auto ff_out = std::ifstream(p_out, std::ios_base::in);
    if(!ff_out.is_open()) throw std::runtime_error("Unexpected");
    line = "";
    while(std::getline(ff_out, line)) lines_out.push_back(line);
    ff_out.close();

    if(lines_in.size() != lines_out.size()) throw std::runtime_error("Unexpected");
    std::vector<std::string>::const_iterator in_ii = lines_in.cbegin();
    std::vector<std::string>::const_iterator out_ii = lines_out.cbegin();

    while(in_ii != lines_in.end()){
        const std::string& in = *in_ii;
        const std::string& out = *out_ii;
        int cmp = in.compare(out);
        if(cmp != 0) {
            auto ff = std::ofstream("/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/debug.log", std::ios_base::out);
            ff << "==========v==========" << std::endl;
            ff << in << std::endl;
            ff << "========= = =========" << std::endl;
            ff << out << std::endl;
            ff << "==========^==========" << std::endl;
            ff.close();
            throw std::runtime_error("Unexpected");
        }
        in_ii++;
        out_ii++;
    }
}

void test_str(){
    std::string p_in = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.s";
    std::string p_out = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.new.s";
    // std::vector<int> sms = {50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90};
    std::vector<int> sms = {90};
    // Go from txt to txt and compare
    for(int sm : sms){
        std::cout << "SM " << sm << "..." << std::flush;
        std::string pp_in = std::vformat(p_in, std::make_format_args(sm));
        std::string pp_out = std::vformat(p_out, std::make_format_args(sm));
        std::cout << "...in" << std::flush;
        const auto t1 = std::chrono::high_resolution_clock::now();
        auto dom = SASS::SASS_Enc_Dom(pp_in, true, false, true);
        const auto t2 = std::chrono::high_resolution_clock::now();
        std::cout << "...out" << std::flush;
        const auto t3 = std::chrono::high_resolution_clock::now();
        dom.dump(pp_out, false, true);
        const auto t4 = std::chrono::high_resolution_clock::now();
        std::cout << " => test..." << std::flush;
        test(pp_in, pp_out);
        std::cout << "ok" << std::endl;
        std::cout << std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << " " << std::chrono::duration_cast<std::chrono::milliseconds>(t4 - t3).count() << std::endl;
    }
}

void test_bin(){
    std::string p_in = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.s";
    std::string p_out = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.bin.s";
    // std::vector<int> sms = {50};
    std::vector<int> sms = {50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90};
    // std::vector<int> sms = {70, 72, 75, 80, 86, 90};
    // Go from txt to bin and compare
    for(int sm : sms){
        std::cout << "SM " << sm << "..." << std::flush;
        std::string pp_in = std::vformat(p_in, std::make_format_args(sm));
        std::string pp_out = std::vformat(p_out, std::make_format_args(sm));
        std::cout << "...in" << std::flush;
        
        const auto t1 = std::chrono::high_resolution_clock::now();
        auto dom = SASS::SASS_Enc_Dom(pp_in, true, false, true);
        const auto t2 = std::chrono::high_resolution_clock::now();
        dom.dump(pp_out, false, false);
        const auto t3 = std::chrono::high_resolution_clock::now();

        std::cout << "...out" << std::flush;
        auto dom2 = SASS::SASS_Enc_Dom(pp_out, true, false, false);
        const auto t4 = std::chrono::high_resolution_clock::now();
        std::cout << " => test..." << std::flush;
        bool cmp = dom == dom2;
        if(!cmp) throw std::runtime_error("Unexpected: dom != dom2");
        const auto t5 = std::chrono::high_resolution_clock::now();

        std::cout << "ok" << std::endl;
        const auto d1 = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
        const auto d2 = std::chrono::duration_cast<std::chrono::milliseconds>(t3 - t2).count();
        const auto d3 = std::chrono::duration_cast<std::chrono::milliseconds>(t4 - t3).count();
        const auto d4 = std::chrono::duration_cast<std::chrono::milliseconds>(t5 - t4).count();
        std::cout << d1 << " " << d2 << " " << d3 << " " << d4 << std::endl;
    }
}

void test_conversion_compressed(){
    std::string p_in_str = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.s";
    std::string p_in = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.bin.s";
    std::string p_out = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.lz4";
    // std::vector<int> sms = {50};
    std::vector<int> sms = {50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90};
    // std::vector<int> sms = {70, 72, 75, 80, 86, 90};
    // Go from txt to bin-non-compressed to bin-compressed and compare
    for(int sm : sms){
        std::cout << "SM " << sm << "..." << std::flush;
        std::string pp_in_str = std::vformat(p_in_str, std::make_format_args(sm));
        std::string pp_in = std::vformat(p_in, std::make_format_args(sm));
        std::string pp_out = std::vformat(p_out, std::make_format_args(sm));
        
        const auto t1 = std::chrono::high_resolution_clock::now();
        auto dom1 = SASS::SASS_Enc_Dom(pp_in_str, true, false, true);
        dom1.dump(pp_out, true, false);
        dom1.dump(pp_in, false, false);
        auto dom2 = SASS::SASS_Enc_Dom(pp_out, true, true, false);
        bool cmp = dom1 == dom2;
        if(!cmp) throw std::runtime_error("bla");
        const auto t2 = std::chrono::high_resolution_clock::now();

        const auto d1 = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
        std::cout << d1 << std::endl;
    }
}

void bin_file_conversion(){
    std::string p = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.lz4";
    // std::vector<int> sms = {50};
    std::vector<int> sms = {52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90};
    // std::vector<int> sms = {70, 72, 75, 80, 86, 90};
    // Go from txt to bin and compare
    for(int sm : sms){
        std::cout << "SM " << sm << "..." << std::flush;
        std::string pp = std::vformat(p, std::make_format_args(sm));

        std::cout << "transcribe: in..." << std::flush;
        const auto t1 = std::chrono::high_resolution_clock::now();
        auto dom = SASS::SASS_Enc_Dom(pp, true, true, false);
        const auto t2 = std::chrono::high_resolution_clock::now();
        std::cout << "out..." << std::flush;
        dom.dump(pp, true, false);
        const auto t3 = std::chrono::high_resolution_clock::now();

        std::cout << "ok" << std::endl;
        const auto d1 = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
        const auto d2 = std::chrono::duration_cast<std::chrono::milliseconds>(t3 - t2).count();
        std::cout << d1 << " " << d2 << std::endl;
    }
}

void test_loader_and_storage(){
    std::string p_in_str = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.s";
    std::string p_in_nc = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.bin.s";
    std::string p_in_lz4 = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/02_OpCodes/DocumentSASS/sm_{0}_domains.lz4";
    // std::vector<int> sms = {50};
    std::vector<int> sms = {50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90};
    // std::vector<int> sms = {90};
    // Load all of them in sequence and check the storage requirement
    for(int sm : sms){
        std::cout << "SM " << sm << "..." << std::endl;
        std::string pp_in_str = std::vformat(p_in_str, std::make_format_args(sm));
        std::string pp_in_nc = std::vformat(p_in_nc, std::make_format_args(sm));
        std::string pp_in_lz4 = std::vformat(p_in_lz4, std::make_format_args(sm));
        
        {
            std::cout << "...txt..." << std::flush;
            const auto t10 = std::chrono::high_resolution_clock::now();
            auto dom0 = SASS::SASS_Enc_Dom(pp_in_str, true, false, true);
            const auto t20 = std::chrono::high_resolution_clock::now();
            const auto d10 = std::chrono::duration_cast<std::chrono::milliseconds>(t20 - t10).count();
            std::cout << d10 << std::endl;
        // }
        // {
        //     std::cout << "...bin-non-compressed..." << std::flush;
        //     const auto t11 = std::chrono::high_resolution_clock::now();
        //     auto dom = SASS::SASS_Enc_Dom(pp_in_nc, true, false, false);
        //     const auto t21 = std::chrono::high_resolution_clock::now();
        //     const auto d11 = std::chrono::duration_cast<std::chrono::milliseconds>(t21 - t11).count();
        //     std::cout << d11 << std::endl;
        // }
        // {
            std::cout << "...bin-compressed..." << std::flush;
            const auto t12 = std::chrono::high_resolution_clock::now();
            auto dom2 = SASS::SASS_Enc_Dom(pp_in_lz4, true, true, false);
            const auto t22 = std::chrono::high_resolution_clock::now();
            const auto d12 = std::chrono::duration_cast<std::chrono::milliseconds>(t22 - t12).count();
            std::cout << d12 << std::endl;

            if(dom0 != dom2) throw std::runtime_error("Unexpected");
        }
    }
}

void test_picker(){
    std::string p_in_str = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/07_PySASS/py_sass/DocumentSASS/sm_{0}_domains.s";
    std::string p_in_lz4 = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/07_PySASS/py_sass/DocumentSASS/sm_{0}_domains.lz4";
    // std::vector<int> sms = {50};
    // std::vector<int> sms = {50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90};
    std::vector<int> sms = {70};
    // Load all of them in sequence and check the storage requirement
    for(int sm : sms){
        std::cout << "SM " << sm << "..." << std::endl;
        std::string pp_in_str = std::vformat(p_in_str, std::make_format_args(sm));
        std::string pp_in_lz4 = std::vformat(p_in_lz4, std::make_format_args(sm));
        {
            auto dom_lz4 = SASS::SASS_Enc_Dom(pp_in_lz4, true, true, false);
            std::string fixed_class = "tex_";
            auto& cc = dom_lz4.domp().at(fixed_class);
            auto& cc_v = dom_lz4.domp_v().at(cc);

            // ['IDEST_SIZE', 'IDEST2_SIZE', 'ISRC_B_SIZE', 'ISRC_A_SIZE'] = (32,32,64,96)
            // [('wmsk', [0, 1, 2, 4, 7, 8, 11, 13, 14]), ('f16rm', [0]), ('dc', [1]), ('lodlc', [2, 3, 4, 5]), ('aoffi', [0]), ('paramA', [1])]
            std::set<int64_t> v_wmsk = {0, 1, 2, 4, 7, 8, 11, 13, 14};
            std::set<int64_t> v_f16rm = {0};
            std::set<int64_t> v_dc = {1};
            std::set<int64_t> v_lodlc = {2, 3, 4, 5};
            std::set<int64_t> v_aoffi = {0};
            std::set<int64_t> v_paramA = {1};

            std::set<SASS::SASS_Bits> wmsk;
            for(const auto& v : v_wmsk) wmsk.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> f16rm;
            for(const auto& v : v_f16rm) f16rm.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> dc;
            for(const auto& v : v_dc) dc.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> lodlc;
            for(const auto& v : v_lodlc) lodlc.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> aoffi;
            for(const auto& v : v_aoffi) aoffi.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> paramA;
            for(const auto& v : v_paramA) paramA.insert(SASS::SASS_Bits::from_int(v));

            // {'Predicate': {'Pu': {...}}, 'Register': {'Rd2': {...}, 'Rd': {...}, 'Rb': {...}}, 'NonZeroRegister': {'Ra': {...}}}
            std::set<int64_t> v_Pu = {0, 1, 2};
            std::set<int64_t> v_Ra = {0, 1, 2, 3, 4, 5, 6, 8, 9, 11};
            std::set<int64_t> v_Rb = {0, 1, 2, 3, 4};
            std::set<int64_t> v_Rd = {0, 1, 2, 3, 4, 5, 6, 8, 9, 11};
            std::set<int64_t> v_Rd2 = {0, 1, 2, 3, 4, 5, 6, 8, 9, 11};

            std::set<SASS::SASS_Bits> Pu;
            for(const auto& v : v_Pu) Pu.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> Ra;
            for(const auto& v : v_Ra) Ra.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> Rb;
            for(const auto& v : v_Rb) Rb.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> Rd;
            for(const auto& v : v_Rd) Rd.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> Rd2;
            for(const auto& v : v_Rd2) Rd2.insert(SASS::SASS_Bits::from_int(v));

            const std::map<std::string, std::set<SASS::SASS_Bits>> ankers = {{"wmsk", wmsk}, {"f16rm", f16rm}, {"dc", dc}, {"lodlc", lodlc}, {"aoffi", aoffi}, {"paramA", paramA}};
            const std::map<std::string, std::set<SASS::SASS_Bits>> exceptions = {{"Pu", Pu}, {"Ra", Ra}, {"Rb", Rb}, {"Rd", Rd}, {"Rd2", Rd2}};
            const auto res_fxed = dom_lz4.fix(fixed_class, ankers, exceptions);

            auto iter = dom_lz4.__fixed_iter(fixed_class);
            std::vector<std::map<std::string, SASS::SASS_Bits>> res;
            while(true){
                bool finished;
                const auto& pick = iter.__next__(finished);
                if(finished) break;
                res.push_back(pick);
            }

            std::set<int64_t> r_wmsk;
            std::set<int64_t> r_f16rm;
            std::set<int64_t> r_dc;
            std::set<int64_t> r_lodlc;
            std::set<int64_t> r_aoffi;
            std::set<int64_t> r_paramA;

            std::set<int64_t> r_Pu;
            std::set<int64_t> r_Ra;
            std::set<int64_t> r_Rb;
            std::set<int64_t> r_Rd;
            std::set<int64_t> r_Rd2;

            for(const auto& r : res){
                // fixed values
                int64_t wmsk_i = SASS::SASS_Bits::__int__(r.at("wmsk"));
                bool f_wmsk = v_wmsk.contains(wmsk_i);
                r_wmsk.insert(wmsk_i);

                int64_t f16rm_i = SASS::SASS_Bits::__int__(r.at("f16rm"));
                bool f_f16rm = v_f16rm.contains(f16rm_i);
                r_f16rm.insert(f16rm_i);

                int64_t dc_i = SASS::SASS_Bits::__int__(r.at("dc"));
                bool f_dc = v_dc.contains(dc_i);
                r_dc.insert(dc_i);

                int64_t lodlc_i = SASS::SASS_Bits::__int__(r.at("lodlc"));
                bool f_lodlc = v_lodlc.contains(lodlc_i);
                r_lodlc.insert(lodlc_i);

                int64_t aoffi_i = SASS::SASS_Bits::__int__(r.at("aoffi"));
                bool f_aoffi = v_aoffi.contains(aoffi_i);
                r_aoffi.insert(aoffi_i);

                int64_t paramA_i = SASS::SASS_Bits::__int__(r.at("paramA"));
                bool f_paramA = v_paramA.contains(paramA_i);
                r_paramA.insert(paramA_i);

                // exceptions
                int64_t Pu_i = SASS::SASS_Bits::__int__(r.at("Pu"));
                bool f_Pu = !v_Pu.contains(Pu_i);
                r_Pu.insert(Pu_i);

                int64_t Ra_i = SASS::SASS_Bits::__int__(r.at("Ra"));
                bool f_Ra = !v_Ra.contains(Ra_i);
                r_Ra.insert(Ra_i);

                int64_t Rb_i = SASS::SASS_Bits::__int__(r.at("Rb"));
                bool f_Rb = !v_Rb.contains(Rb_i);
                r_Rb.insert(Rb_i);

                int64_t Rd_i = SASS::SASS_Bits::__int__(r.at("Rd"));
                bool f_Rd = !v_Rd.contains(Rd_i);
                r_Rd.insert(Rd_i);

                int64_t Rd2_i = SASS::SASS_Bits::__int__(r.at("Rd2"));
                bool f_Rd2 = !v_Rd2.contains(Rd2_i);
                r_Rd2.insert(Rd2_i);

                bool ok = f_wmsk && f_f16rm && f_dc && f_lodlc && f_aoffi && f_paramA && f_Pu && f_Ra && f_Rb && f_Rd && f_Rd2;
                if(!ok){
                    throw std::runtime_error("Wrong value found...");
                }
            }

            std::set<int64_t> ii_wmsk;
            std::set_intersection(r_wmsk.begin(), r_wmsk.end(), v_wmsk.begin(), v_wmsk.end(), std::inserter(ii_wmsk, ii_wmsk.begin()));
            std::set<int64_t> ii_f16rm;
            std::set_intersection(r_f16rm.begin(), r_f16rm.end(), v_f16rm.begin(), v_f16rm.end(), std::inserter(ii_f16rm, ii_f16rm.begin()));
            std::set<int64_t> ii_dc;
            std::set_intersection(r_dc.begin(), r_dc.end(), v_dc.begin(), v_dc.end(), std::inserter(ii_dc, ii_dc.begin()));
            std::set<int64_t> ii_lodlc;
            std::set_intersection(r_lodlc.begin(), r_lodlc.end(), v_lodlc.begin(), v_lodlc.end(), std::inserter(ii_lodlc, ii_lodlc.begin()));
            std::set<int64_t> ii_aoffi;
            std::set_intersection(r_aoffi.begin(), r_aoffi.end(), v_aoffi.begin(), v_aoffi.end(), std::inserter(ii_aoffi, ii_aoffi.begin()));
            std::set<int64_t> ii_paramA;
            std::set_intersection(r_paramA.begin(), r_paramA.end(), v_paramA.begin(), v_paramA.end(), std::inserter(ii_paramA, ii_paramA.begin()));

            bool complete_wmsk = ii_wmsk == r_wmsk;
            bool complete_f16rm = ii_f16rm == r_f16rm;
            bool complete_dc = ii_dc == r_dc;
            bool complete_lodlc = ii_lodlc == r_lodlc;
            bool complete_aoffi = ii_aoffi == r_aoffi;
            bool complete_paramA = ii_paramA == r_paramA;
            bool complete_ok = complete_wmsk && complete_f16rm && complete_dc && complete_lodlc && complete_aoffi && complete_paramA;

            if(!complete_ok){
                throw std::runtime_error("Incomplete value set found...");
            }

            std::cout << "lol" << std::endl;

            // std::cout << "load text..." << std::endl;
            // auto dom_str = SASS::SASS_Enc_Dom(pp_in_str, true, false, true);

            // std::cout << "compare..." << std::endl;
            // if(dom_lz4 != dom_str) throw std::runtime_error("Unexpected");

            // std::vector<std::map<std::string, SASS::SASS_Bits>> res;
            // for(const auto& instr : dom.domp()){
            //     std::cout << instr.first << std::endl;
            //     for(int i=0; i<5000; ++i){
            //         const auto r = dom.pick(instr.first);
            //         res.push_back(r);
            //         // for(const auto& enc : res){
            //         //     std::cout << enc.first << ": " << SASS::SASS_Bits::__str__(enc.second) << ", ";
            //         // }
            //         // std::cout << std::endl;
            //     }
            // }
            // for(int i=0; i<50; ++i){
            //     const auto res = dom.pick("TEX_B");
            //     for(const auto& enc : res){
            //         std::cout << enc.first << ": " << SASS::SASS_Bits::__str__(enc.second) << ", ";
            //     }
            //     std::cout << std::endl;
            // }
        }
    }
}

void test_picker2(){
    std::string p_in_str = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/07_PySASS/py_sass/DocumentSASS/sm_{0}_domains.s";
    std::string p_in_lz4 = "/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/07_PySASS/py_sass/DocumentSASS/sm_{0}_domains.lz4";
    // std::vector<int> sms = {50};
    // std::vector<int> sms = {50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90};
    std::vector<int> sms = {70};
    // Load all of them in sequence and check the storage requirement
    for(int sm : sms){
        std::cout << "SM " << sm << "..." << std::endl;
        std::string pp_in_str = std::vformat(p_in_str, std::make_format_args(sm));
        std::string pp_in_lz4 = std::vformat(p_in_lz4, std::make_format_args(sm));
        {
            auto dom_lz4 = SASS::SASS_Enc_Dom(pp_in_lz4, true, true, false);
            std::string fixed_class = "tex_";
            auto& cc = dom_lz4.domp().at(fixed_class);
            auto& cc_v = dom_lz4.domp_v().at(cc);

            // ['IDEST_SIZE', 'IDEST2_SIZE', 'ISRC_B_SIZE', 'ISRC_A_SIZE'] = (32,32,64,96)
            // [('wmsk', [0, 1, 2, 4, 7, 8, 11, 13, 14]), ('f16rm', [0]), ('dc', [1]), ('lodlc', [2, 3, 4, 5]), ('aoffi', [0]), ('paramA', [1])]
            std::set<int64_t> v_wmsk = {0, 1, 2, 4, 7, 8, 11, 13, 14};
            std::set<int64_t> v_f16rm = {0};
            std::set<int64_t> v_dc = {1};
            std::set<int64_t> v_lodlc = {2, 3, 4, 5};
            std::set<int64_t> v_aoffi = {0};
            std::set<int64_t> v_paramA = {1};

            std::set<SASS::SASS_Bits> wmsk;
            for(const auto& v : v_wmsk) wmsk.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> f16rm;
            for(const auto& v : v_f16rm) f16rm.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> dc;
            for(const auto& v : v_dc) dc.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> lodlc;
            for(const auto& v : v_lodlc) lodlc.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> aoffi;
            for(const auto& v : v_aoffi) aoffi.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> paramA;
            for(const auto& v : v_paramA) paramA.insert(SASS::SASS_Bits::from_int(v));

            // {'Predicate': {'Pu': {...}}, 'Register': {'Rd2': {...}, 'Rd': {...}, 'Rb': {...}}, 'NonZeroRegister': {'Ra': {...}}}
            std::set<int64_t> v_Pu = {0, 1, 2};
            std::set<int64_t> v_Ra = {0, 1, 2, 3, 4, 5, 6, 8, 9, 11};
            std::set<int64_t> v_Rb = {0, 1, 2, 3, 4};
            std::set<int64_t> v_Rd = {0, 1, 2, 3, 4, 5, 6, 8, 9, 11};
            std::set<int64_t> v_Rd2 = {0, 1, 2, 3, 4, 5, 6, 8, 9, 11};

            std::set<SASS::SASS_Bits> Pu;
            for(const auto& v : v_Pu) Pu.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> Ra;
            for(const auto& v : v_Ra) Ra.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> Rb;
            for(const auto& v : v_Rb) Rb.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> Rd;
            for(const auto& v : v_Rd) Rd.insert(SASS::SASS_Bits::from_int(v));
            std::set<SASS::SASS_Bits> Rd2;
            for(const auto& v : v_Rd2) Rd2.insert(SASS::SASS_Bits::from_int(v));

            const std::map<std::string, std::set<SASS::SASS_Bits>> ankers = {{"wmsk", wmsk}, {"f16rm", f16rm}, {"dc", dc}, {"lodlc", lodlc}, {"aoffi", aoffi}, {"paramA", paramA}};
            // auto iter = dom_lz4.__fixed_iter2(fixed_class, ankers);

            // const std::map<std::string, std::set<SASS::SASS_Bits>> exceptions = {{"Pu", Pu}, {"Ra", Ra}, {"Rb", Rb}, {"Rd", Rd}, {"Rd2", Rd2}};
            // const auto res_fxed = dom_lz4.fix(fixed_class, ankers, exceptions);

            std::vector<std::string> keys;
            std::vector<std::vector<SASS::SASS_Bits>> values;
            for(const auto& p : ankers){
                keys.push_back(p.first);
                values.push_back(std::vector<SASS::SASS_Bits>(p.second.begin(), p.second.end()));
            }
            // how to map the two systems
            auto product = SASS::SASS_Enc_Dom::cart_product(values);
            auto product_inds = SASS::SASS_Enc_Dom::cart_product_by_inds(values);
            bool same = true;
            for(size_t outer_ind=0; outer_ind<product_inds.size(); ++outer_ind){
                for(size_t col_ind=0; col_ind<product_inds.at(outer_ind).size(); ++col_ind){
                    int row_ind = outer_ind;
                    int value_ind = product_inds.at(row_ind).at(col_ind);

                    auto bb1 = values.at(col_ind).at(value_ind);
                    auto bb2 = product.at(row_ind).at(col_ind);
                    if(bb1 != bb2) same = false;
                }
            }

            auto iter = dom_lz4.__fixed_iter2(fixed_class, ankers);
            std::vector<std::map<std::string, SASS::SASS_Bits>> res;
            size_t counter = 0;
            while(true){
                if(counter == 1000000) break;
                bool finished;
                const auto& pick = iter.__next__(finished);
                if(finished) break;
                res.push_back(pick);
                counter++;
            }

            std::set<int64_t> r_wmsk;
            std::set<int64_t> r_f16rm;
            std::set<int64_t> r_dc;
            std::set<int64_t> r_lodlc;
            std::set<int64_t> r_aoffi;
            std::set<int64_t> r_paramA;

            std::set<int64_t> r_Pu;
            std::set<int64_t> r_Ra;
            std::set<int64_t> r_Rb;
            std::set<int64_t> r_Rd;
            std::set<int64_t> r_Rd2;

            for(const auto& r : res){
                // fixed values
                int64_t wmsk_i = SASS::SASS_Bits::__int__(r.at("wmsk"));
                bool f_wmsk = v_wmsk.contains(wmsk_i);
                r_wmsk.insert(wmsk_i);

                int64_t f16rm_i = SASS::SASS_Bits::__int__(r.at("f16rm"));
                bool f_f16rm = v_f16rm.contains(f16rm_i);
                r_f16rm.insert(f16rm_i);

                int64_t dc_i = SASS::SASS_Bits::__int__(r.at("dc"));
                bool f_dc = v_dc.contains(dc_i);
                r_dc.insert(dc_i);

                int64_t lodlc_i = SASS::SASS_Bits::__int__(r.at("lodlc"));
                bool f_lodlc = v_lodlc.contains(lodlc_i);
                r_lodlc.insert(lodlc_i);

                int64_t aoffi_i = SASS::SASS_Bits::__int__(r.at("aoffi"));
                bool f_aoffi = v_aoffi.contains(aoffi_i);
                r_aoffi.insert(aoffi_i);

                int64_t paramA_i = SASS::SASS_Bits::__int__(r.at("paramA"));
                bool f_paramA = v_paramA.contains(paramA_i);
                r_paramA.insert(paramA_i);

                bool ok = f_wmsk && f_f16rm && f_dc && f_lodlc && f_aoffi && f_paramA; // && f_Pu && f_Ra && f_Rb && f_Rd && f_Rd2;
                if(!ok){
                    throw std::runtime_error("Wrong value found...");
                }
            }

            std::set<int64_t> ii_wmsk;
            std::set_intersection(r_wmsk.begin(), r_wmsk.end(), v_wmsk.begin(), v_wmsk.end(), std::inserter(ii_wmsk, ii_wmsk.begin()));
            std::set<int64_t> ii_f16rm;
            std::set_intersection(r_f16rm.begin(), r_f16rm.end(), v_f16rm.begin(), v_f16rm.end(), std::inserter(ii_f16rm, ii_f16rm.begin()));
            std::set<int64_t> ii_dc;
            std::set_intersection(r_dc.begin(), r_dc.end(), v_dc.begin(), v_dc.end(), std::inserter(ii_dc, ii_dc.begin()));
            std::set<int64_t> ii_lodlc;
            std::set_intersection(r_lodlc.begin(), r_lodlc.end(), v_lodlc.begin(), v_lodlc.end(), std::inserter(ii_lodlc, ii_lodlc.begin()));
            std::set<int64_t> ii_aoffi;
            std::set_intersection(r_aoffi.begin(), r_aoffi.end(), v_aoffi.begin(), v_aoffi.end(), std::inserter(ii_aoffi, ii_aoffi.begin()));
            std::set<int64_t> ii_paramA;
            std::set_intersection(r_paramA.begin(), r_paramA.end(), v_paramA.begin(), v_paramA.end(), std::inserter(ii_paramA, ii_paramA.begin()));

            bool complete_wmsk = ii_wmsk == r_wmsk;
            bool complete_f16rm = ii_f16rm == r_f16rm;
            bool complete_dc = ii_dc == r_dc;
            bool complete_lodlc = ii_lodlc == r_lodlc;
            bool complete_aoffi = ii_aoffi == r_aoffi;
            bool complete_paramA = ii_paramA == r_paramA;
            bool complete_ok = complete_wmsk && complete_f16rm && complete_dc && complete_lodlc && complete_aoffi && complete_paramA;

            if(!complete_ok){
                throw std::runtime_error("Incomplete value set found...");
            }

            // std::cout << "lol" << std::endl;

            // // std::cout << "load text..." << std::endl;
            // // auto dom_str = SASS::SASS_Enc_Dom(pp_in_str, true, false, true);

            // // std::cout << "compare..." << std::endl;
            // // if(dom_lz4 != dom_str) throw std::runtime_error("Unexpected");

            // // std::vector<std::map<std::string, SASS::SASS_Bits>> res;
            // // for(const auto& instr : dom.domp()){
            // //     std::cout << instr.first << std::endl;
            // //     for(int i=0; i<5000; ++i){
            // //         const auto r = dom.pick(instr.first);
            // //         res.push_back(r);
            // //         // for(const auto& enc : res){
            // //         //     std::cout << enc.first << ": " << SASS::SASS_Bits::__str__(enc.second) << ", ";
            // //         // }
            // //         // std::cout << std::endl;
            // //     }
            // // }
            // // for(int i=0; i<50; ++i){
            // //     const auto res = dom.pick("TEX_B");
            // //     for(const auto& enc : res){
            // //         std::cout << enc.first << ": " << SASS::SASS_Bits::__str__(enc.second) << ", ";
            // //     }
            // //     std::cout << std::endl;
            // // }
        }
    }
}

int main(int argc, char** argv){
    test_picker2();
    return 0;
}