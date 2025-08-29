#include <tuple>
#include <algorithm>
#include <vector>
#include <cinttypes>
#include <iostream>
#include <span>
#include <cstring>
#include <variant>
#include <type_traits>
#include <assert.h>

#include "../src/Utils.hpp"
#include "../src/Pickle.hpp"

using namespace SASS;

int main()
{
    using Test_Type_0 = std::tuple<std::string, std::string, int, float, double>;
    using Test_Type =  std::variant<Test_Type_0>;

    using Test_Type2_0 = std::tuple<int, float, double>;
    using Test_Type2 = std::variant<Test_Type2_0>;

    using Test_Type3_0 = std::tuple<float, int, double>;
    using Test_Type3_1 = std::tuple<bool, int, double>;
    using Test_Type3 = std::variant<Test_Type3_0, Test_Type3_1>;

    using Test_Type4_0 = std::tuple<float, std::vector<Test_Type3>, double>;
    using Test_Type4 = std::variant<Test_Type4_0>;

    using Test_Type6_0 = std::tuple<float, std::vector<Test_Type3>, TOptions>;
    using Test_Type6 = std::variant<Test_Type6_0>;

    using Test_Type8_0 = std::tuple<float, int, TOptions>;
    using Test_Type8_1 = std::tuple<float, float, TOptions>;
    using Test_Type8_2 = std::tuple<float, double, TOptions>;
    using Test_Type8 = std::variant<Test_Type8_0, Test_Type8_1, Test_Type8_2>;

    using Test_Type9_0 = std::tuple<float, int, TOptionsSet>;
    using Test_Type9_1 = std::tuple<float, int, TStrOptionsSet>;
    using Test_Type9 = std::variant<Test_Type9_0, Test_Type9_1>;

    using TVarVector = std::vector<std::variant<int, float>>;
    using Test_Type10_0 = std::tuple<std::string, TVarVector, bool>;
    using Test_Type10 = std::variant<Test_Type10_0>;

    Test_Type t2 = Test_Type_0{"oh no, am I in the way?", "this is so embarassing...", 15, 11.3f, 19.7};
    Test_Type2 t3 = Test_Type2_0{15, 11.3f, 19.7};
    Test_Type3 t4 = Test_Type3_0{11.3f, 15, 19.7};
    Test_Type4 t5 = Test_Type4_0{11.3f, {Test_Type3_0{11.3f, 1, 19.7}, Test_Type3_0{11.3f, 2, 19.7}, Test_Type3_0{11.3f, 3, 19.7}}, 19.7};
    Test_Type6 t7 = Test_Type6_0{11.3f, {Test_Type3_1{false, 1, 12.7}}, {{"R1", {1}}, {"R2", {2}}}};
    TOptions o = {{"R1", {1}}, {"R2", {2}}};
    TStrOptionsSet tsos = {"R1", "R2"};
    TOptionsSet tios = {0, 1, 2, 3, 4};

    Test_Type8 t8_0 = Test_Type8_1{11.3f, 12.1f, o};
    Test_Type8 t8_1 = Test_Type8_0{11.3f, 12, o};
    Test_Type8 t8_2 = Test_Type8_0{11.3f, 12.3, o};

    Test_Type9 t9_0 = Test_Type9_0{10.1, 2, tios};
    Test_Type9 t9_1 = Test_Type9_1{10.1, 2, tsos};

    Test_Type10 t10_0 = Test_Type10_0{"hello world", TVarVector{2, 1.0f, 10}, false};


    TVec v2 = Pickle::dumps(t2);
    TVec v3 = Pickle::dumps(t3);
    TVec v4 = Pickle::dumps(t4);
    TVec v5 = Pickle::dumps(t5);
    TVec v7 = Pickle::dumps(t7);
    TVec v8_0 = Pickle::dumps(t8_0);
    TVec v8_1 = Pickle::dumps(t8_1);
    TVec v8_2 = Pickle::dumps(t8_2);
    TVec v9_0 = Pickle::dumps(t9_0);
    TVec v9_1 = Pickle::dumps(t9_1);
    TVec v10_0 = Pickle::dumps(t10_0);

    Test_Type3 res4 = Pickle::loads<Test_Type3>(v4);
    Test_Type2 res3 = Pickle::loads<Test_Type2>(v3);
    Test_Type res2 =  Pickle::loads<Test_Type>(v2);
    Test_Type4 res5 = Pickle::loads<Test_Type4>(v5);
    Test_Type6 res7 = Pickle::loads<Test_Type6>(v7);
    Test_Type8 res8_0 = Pickle::loads<Test_Type8>(v8_0);
    Test_Type8 res8_1 = Pickle::loads<Test_Type8>(v8_1);
    Test_Type8 res8_2 = Pickle::loads<Test_Type8>(v8_2);
    Test_Type9 res9_0 = Pickle::loads<Test_Type9>(v9_0);
    Test_Type9 res9_1 = Pickle::loads<Test_Type9>(v9_1);
    Test_Type10 res10_0 = Pickle::loads<Test_Type10>(v10_0);

    bool check2 = res2 == t2;
    bool check3 = res3 == t3;
    bool check4 = res4 == t4;
    bool check5 = res5 == t5;
    bool check7 = res7 == t7;
    bool check8_0 = res8_0 == t8_0;
    bool check8_1 = res8_1 == t8_1;
    bool check8_2 = res8_2 == t8_2;
    bool check9_0 = res9_0 == t9_0;
    bool check9_1 = res9_1 == t9_1;
    bool check10_0 = res10_0 == t10_0;

    // { auto x = Pck::get<0>(res2); }
    // { auto x = Pck::get<1>(res2); }
    // { auto x = Pck::get<2>(res2); }

    // { auto x = Pck::get<0>(res3); }
    // { auto x = Pck::get<1>(res3); }
    // { auto x = Pck::get<2>(res3); }

    // { auto x = Pck::get<0>(res4); }
    // { auto x = Pck::get<1>(res4); }
    // { auto x = Pck::get<2>(res4); }

    // { auto x = Pck::get<0>(res5); }
    // { auto x = Pck::get<1>(res5); }
    // { auto x = Pck::get<2>(res5); }

    // { auto x = Pck::get<0>(res7); }
    // { auto x = Pck::get<1>(res7); }
    // { auto x = Pck::get<2>(res7); }

    // { auto x = Pck::get<0>(res8); }
    // { auto x = Pck::get<1>(res8); }
    // { auto x = Pck::get<2>(res8); }

    // { auto x = std::visit([&](const auto& k){ return k; }, res8); }

    assert(check2);
    assert(check3);
    assert(check4);
    assert(check5);
    assert(check7);
    assert(check8_0);
    assert(check8_1);
    assert(check8_2);
    assert(check9_0);
    assert(check9_1);
    assert(check10_0);

    // std::vector<Test_Type> vec = {
    //     {"oh no, am I in the way?", "this is so embarassing...", 1, 11.3f, 19.7}, 
    //     {"oh no, am I in the way?", "this is so embarassing...", 2, 11.3f, 19.7},
    //     {"oh no, am I in the way?", "this is so embarassing...", 3, 11.3f, 19.7},
    //     {"oh no, am I in the way?", "this is so embarassing...", 4, 11.3f, 19.7}
    // };

    // TVec v6 = ToBytes::tuple_vec_to_vector(vec);
    // std::vector<Test_Type> res6 = ToData::vector_2_tuple_vec<Test_Type>(v6);

    return 0;
}