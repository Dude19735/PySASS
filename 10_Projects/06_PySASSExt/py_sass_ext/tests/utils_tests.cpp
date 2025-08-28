#include <vector>
#include <assert.h>
#include "../src/Utils.hpp"
#include "../src/TT_Terms.hpp"

void test_strip() {
    std::string ws1 = "  hello world ";
    std::string ws2 = "  hello world\n ";
    std::string ws_res = "hello world";

    std::string wres1 = SASS::Utils::strip(ws1);
    std::string wres2 = SASS::Utils::strip(ws2);
    assert(ws_res.compare(wres1) == 0);
    assert(ws_res.compare(wres2) == 0);

    std::string cs = "\"hello world\"\n";
    std::string cs1 = "hello world\"\n";
    std::string cs2 = "\"hello world\"";
    std::string cs3 = "hello world\"";
    std::string cs4 = "hello world";

    std::string res1 = SASS::Utils::strip(cs, '"');
    assert(res1.compare(cs1) == 0);
    std::string res2 = SASS::Utils::strip(cs, '\n');
    assert(res2.compare(cs2) == 0);
    std::string res3 = SASS::Utils::strip(cs1, '\n');
    assert(cs3.compare(res3) == 0);
    std::string res4 = SASS::Utils::strip(cs2, '"');
    assert(cs4.compare(res4) == 0);
}   

void test_split() {
    std::string a = "hello world, blablabla";
    std::vector<std::string> resa = SASS::Utils::split(a);
    assert(resa.size() == 3);
    assert(resa.at(0).compare("hello") == 0);
    assert(resa.at(1).compare("world,") == 0);
    assert(resa.at(2).compare("blablabla") == 0);

    std::vector<std::string> resb = SASS::Utils::split(a, ',');
    assert(resb.size() == 2);
    assert(resb.at(0).compare("hello world") == 0);
    assert(resb.at(1).compare(" blablabla") == 0);

    std::vector<std::string> resc = SASS::Utils::split("hello", '/');
    assert(resc.size() == 1);
    assert(resc.at(0).compare("hello") == 0);
}

void test_convert() {
    {
        SASS::TConvertVariant res = SASS::Utils::try_convert("0x000000", true);
        assert(std::holds_alternative<int>(res));
        assert(std::get<int>(res) == 0);
    }
    {
        SASS::TConvertVariant res = SASS::Utils::try_convert("0x000000");
        assert(std::holds_alternative<std::string>(res));
        assert(std::get<std::string>(res).compare("0x000000") == 0);
    }
    {
        SASS::TConvertVariant res = SASS::Utils::try_convert("1.0f");
        assert(std::holds_alternative<float>(res));
        assert(std::get<float>(res) == 1.0f);
    }
    {
        SASS::TConvertVariant res = SASS::Utils::try_convert("0b01101", false, true);
        assert(std::holds_alternative<int>(res));
        assert(std::get<int>(res) == 13);
    }
    {
        SASS::TConvertVariant res = SASS::Utils::try_convert("0b01101", false, false);
        assert(std::holds_alternative<std::string>(res));
        assert(std::get<std::string>(res).compare("0b01101") == 0);
    }
    {
        SASS::TConvertVariant res = SASS::Utils::try_convert("0b01_101", false, true, true);
        assert(std::holds_alternative<int>(res));
        assert(std::get<int>(res) == 13);
    }
    {
        SASS::TConvertVariant res = SASS::Utils::try_convert("0b01_101", false, true);
        assert(std::holds_alternative<std::string>(res));
        assert(std::get<std::string>(res).compare("0b01_101") == 0);
    }
    {
        SASS::TConvertVariant res = SASS::Utils::try_convert("True");
        assert(std::holds_alternative<bool>(res));
        assert(std::get<bool>(res) == true);
    }
    {
        SASS::TConvertVariant res = SASS::Utils::try_convert("False");
        assert(std::holds_alternative<bool>(res));
        assert(std::get<bool>(res) == false);
    }
}

int main(int argc, char** argv) {

    test_strip();
    test_split();
    test_convert();

    auto x = SASS::TT_Alias(std::string("hello"));
    auto x_bytes = SASS::Pickle::dumps(x.get_state());
    auto x_state = SASS::Pickle::loads<SASS::TT_Alias_State>(x_bytes);

    auto x2 = SASS::TT_OpAtNot("lol");
    auto x3 = SASS::TT_OpCashQuestion();
    auto x4 = SASS::TT_OpCashAnd();
    auto x5 = SASS::TT_OpCashAssign();

    auto x6 = SASS::TT_Default("Register", false, {{"R1", {1}}, {"R2", {2}}});
    {
        auto x7 = SASS::TT_Default(3, false, {{"R0",{0}}, {"R1",{1}}, {"R2",{2}}, {"R3",{3}}, {"R4",{4}}, {"R5",{5}}, {"R6",{6}}, {"R7",{7}}});
        auto x7_bytes = SASS::Pickle::dumps(x7.get_state());
        auto x7_state = SASS::Pickle::loads<SASS::TT_Default_State>(x7_bytes);
    }

    auto func_arg = SASS::TT_FuncArg(5, false, false, 5, false, 0, false, 0);
    {
        auto xb = SASS::Pickle::dumps(func_arg.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_FuncArg_State>(xb);
    }
    {
        auto f = SASS::TT_Func("hello", "SImm", {}, func_arg, false, false, x);
        auto xb = SASS::Pickle::dumps(f.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_Func_State>(xb);
    }
    {
        auto f = SASS::TT_Func("hello", "SImm", {"SImm", "UImm", "F64Imm"}, func_arg, false, false, x);
        auto xb = SASS::Pickle::dumps(f.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_Func_State>(xb);
    }
    {
        auto f = SASS::TT_Reg("ccc", 0, x6, {{"R1", {1}}, {"R2", {2}}}, x);
        auto xb = SASS::Pickle::dumps(f.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_Reg_State>(xb);
    }
    {
        auto f = SASS::TT_ICode("1010", {12, 25, 34, 56}, {1,0,1,0});
        auto xb = SASS::Pickle::dumps(f.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_ICode_State>(xb);
    }
    {
        auto reg = SASS::TT_Reg("ccc", 0, x6, {{"R1", {1}}, {"R2", {2}}}, x);
        auto ext = SASS::TT_Ext("blabla", x, reg, x6, false);
        auto param = SASS::TT_Param("blaaaaa", x, {SASS::TT_OpAtAbs("Pg")}, reg, {ext}, false, false);
        auto f = SASS::TT_Cash("1010", {SASS::TT_OpCashAnd(), SASS::TT_OpCashAssign(), param , SASS::TT_OpCashQuestion()});

        auto xb = SASS::Pickle::dumps(f.get_state());
        SASS::TT_Cash_State xs = SASS::Pickle::loads<SASS::TT_Cash_State>(xb);

        SASS::TT_Cash_State_0 state0 = std::get<SASS::TT_Cash_State_0>(xs);
        std::string class_name = std::get<0>(state0);
        SASS::TCashStateVec cash_state_vec = std::get<1>(state0);
        SASS::TCashVec cash_vec = SASS::TT_Cash::muvh<SASS::TCashType, SASS::TCashStateType, SASS::cash_type_size>(cash_state_vec);
        bool added_later = std::get<2>(state0);
        std::cout << f.__str__() << std::endl;
        auto f2 = SASS::TT_Cash(class_name, cash_vec, added_later);
        std::cout << f2.__str__() << std::endl;
    }

    // auto f2 = SASS::TT_Func("hellooooooooooooooooooooooooooooooo", "SImm", {}, SASS::TT_FuncArg(5, false, false, 5, false, 0, false, 0), false, false, SASS::TT_Alias(std::string("hwllo world")));
    // auto t = std::make_tuple<SASS::TT_Func>(std::move(f));
    
    return 0;
}