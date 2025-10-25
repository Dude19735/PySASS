#include <vector>
#include <assert.h>
#include "../src/Utils.hpp"
#include "../src/TT_Terms.hpp"
#include "../src/TT_Instruction.hpp"

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

    auto x = SASS::TT_Alias(std::string("hello"), false);
    auto x_bytes = SASS::Pickle::dumps(x.get_state());
    auto x_state = SASS::Pickle::loads<SASS::TT_Alias_State>(x_bytes);
    {
        SASS::TT_Alias* reca = reinterpret_cast<SASS::TT_Alias*>(new uint8_t[sizeof(SASS::TT_Alias)]);
        SASS::TT_Alias::unpack(*reca, x_bytes, std::make_index_sequence<SASS::tt_alias_state_size>{});
        bool comp = (x == *reca);
        assert(comp == true);
        delete reca;
    }

    auto x2 = SASS::TT_OpAtNot("lol");
    auto x3 = SASS::TT_OpCashQuestion();
    auto x4 = SASS::TT_OpCashAnd();
    auto x5 = SASS::TT_OpCashAssign();

    auto x6 = SASS::TT_Default("R1", false, {{"R1", {1}}, {"R2", {2}}});
    {
        auto x7 = SASS::TT_Default("R3", false, {{"R0",{0}}, {"R1",{1}}, {"R2",{2}}, {"R3",{3}}, {"R4",{4}}, {"R5",{5}}, {"R6",{6}}, {"R7",{7}}});
        auto x7_bytes = SASS::Pickle::dumps(x7.get_state());
        auto x7_state = SASS::Pickle::loads<SASS::TT_Default_State>(x7_bytes);
        {
            SASS::TT_Default* reca = reinterpret_cast<SASS::TT_Default*>(new uint8_t[sizeof(SASS::TT_Default)]);
            SASS::TT_Default::unpack(*reca, x7_bytes, std::make_index_sequence<SASS::tt_default_state_size>{});
            bool comp = (x7 == *reca);
            assert(comp == true);
            delete reca;
        }
    }

    auto func_arg = SASS::TT_FuncArg(5, false, false, 5, false, 0, false, 0);
    {
        auto xb = SASS::Pickle::dumps(func_arg.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_FuncArg_State>(xb);
        {
            SASS::TT_FuncArg* reca = reinterpret_cast<SASS::TT_FuncArg*>(new uint8_t[sizeof(SASS::TT_FuncArg)]);
            SASS::TT_FuncArg::unpack(*reca, xb, std::make_index_sequence<SASS::tt_funcarg_state_size>{});
            bool comp = (func_arg == *reca);
            assert(comp == true);
            delete reca;
        }
    }
    {
        auto f = SASS::TT_Func("SImm", {}, func_arg, false, false, x);
        auto xb = SASS::Pickle::dumps(f.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_Func_State>(xb);
        {
            SASS::TT_Func* reca = reinterpret_cast<SASS::TT_Func*>(new uint8_t[sizeof(SASS::TT_Func)]);
            SASS::TT_Func::unpack(*reca, xb, std::make_index_sequence<SASS::tt_func_state_size>{});
            bool comp = (f == *reca);
            assert(comp == true);
            delete reca;
        }
    }
    {
        auto f = SASS::TT_Func("SImm", {"SImm", "UImm", "F64Imm"}, func_arg, false, false, x);
        auto xb = SASS::Pickle::dumps(f.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_Func_State>(xb);
        {
            SASS::TT_Func* reca = reinterpret_cast<SASS::TT_Func*>(new uint8_t[sizeof(SASS::TT_Func)]);
            SASS::TT_Func::unpack(*reca, xb, std::make_index_sequence<SASS::tt_func_state_size>{});
            bool comp = (f == *reca);
            assert(comp == true);
            delete reca;
        }
    }
    {
        auto f = SASS::TT_Reg("Register", x6, x);
        auto xb = SASS::Pickle::dumps(f.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_Reg_State>(xb);
        {
            SASS::TT_Reg* reca = reinterpret_cast<SASS::TT_Reg*>(new uint8_t[sizeof(SASS::TT_Reg)]);
            SASS::TT_Reg::unpack(*reca, xb, std::make_index_sequence<SASS::tt_reg_state_size>{});
            bool comp = (f == *reca);
            assert(comp == true);
            delete reca;
        }
    }
    {
        auto f = SASS::TT_ICode("1010", {12, 25, 34, 56}, {1,0,1,0});
        auto xb = SASS::Pickle::dumps(f.get_state());
        auto xs = SASS::Pickle::loads<SASS::TT_ICode_State>(xb);
        {
            SASS::TT_ICode* reca = reinterpret_cast<SASS::TT_ICode*>(new uint8_t[sizeof(SASS::TT_ICode)]);
            SASS::TT_ICode::unpack(*reca, xb, std::make_index_sequence<SASS::tt_icode_state_size>{});
            bool comp = (f == *reca);
            assert(comp == true);
            delete reca;
        }
    }
    {
        auto reg = SASS::TT_Reg("Register", x6, x);
        auto ext = SASS::TT_Ext(reg);
        auto param = SASS::TT_Param({SASS::TT_OpAtAbs("Pg")}, reg, {ext});
        auto f = SASS::TT_Cash({SASS::TT_OpCashAnd(), SASS::TT_OpCashAssign(), param , SASS::TT_OpCashQuestion()});

        auto xb = SASS::Pickle::dumps(f.get_state());
        SASS::TT_Cash_State xs = SASS::Pickle::loads<SASS::TT_Cash_State>(xb);

        SASS::TT_Cash_State_0 state0 = std::get<SASS::TT_Cash_State_0>(xs);
        SASS::TCashComponentsStateVec cash_state_vec = std::get<0>(state0);
        SASS::TCashComponentsVec cash_vec = SASS::TT_Cash::muv_vec_h<SASS::TCashComponentType, SASS::TCashComponentStateType, SASS::cash_type_size>(cash_state_vec);
        bool added_later = std::get<1>(state0);
        std::cout << f.__str__() << std::endl;
        auto f2 = SASS::TT_Cash(cash_vec, added_later);
        std::cout << f2.__str__() << std::endl;

        {
            SASS::TT_Cash* reca = reinterpret_cast<SASS::TT_Cash*>(new uint8_t[sizeof(SASS::TT_Cash)]);
            SASS::TT_Cash::unpack(*reca, xb, std::make_index_sequence<SASS::tt_cash_state_size>{});
            bool comp = (f == *reca);
            assert(comp == true);
            delete reca;
        }
    }
    {
        auto alias = SASS::TT_Alias("hello", false);
        auto reg = SASS::TT_Reg("Register", x6, x);
        auto func = SASS::TT_Func("SImm", {"SImm", "UImm", "F64Imm"}, func_arg, false, false, x);
        auto ext = SASS::TT_Ext(reg);
        auto param1 = SASS::TT_Param({SASS::TT_OpAtAbs("Pg")}, reg, {ext});
        auto param2 = SASS::TT_Param({SASS::TT_OpAtNegate("Pg")}, func, {ext});
        auto ops_vec = SASS::TOpsVec{ SASS::TT_OpAtNot("lol"), SASS::TT_OpAtAbs("lol"), SASS::TT_OpAtInvert("lol") };
        auto params = SASS::TParamVec {param1, param2};
        auto list = SASS::TT_List(params, SASS::TExtVec{ ext });

        auto xb = SASS::Pickle::dumps(list.get_state());
        SASS::TT_List_State xs = SASS::Pickle::loads<SASS::TT_List_State>(xb);
        std::cout << list.__str__() << std::endl;

        {
            SASS::TT_List* reca = reinterpret_cast<SASS::TT_List*>(new uint8_t[sizeof(SASS::TT_List)]);
            SASS::TT_List::unpack(*reca, xb, std::make_index_sequence<SASS::tt_list_state_size>{});
            bool comp = (list == *reca);
            assert(comp == true);
            delete reca;
        }
    }
    {
        auto alias = SASS::TT_Alias("hello", false);
        auto reg = SASS::TT_Reg("Register", x6, x);
        auto func = SASS::TT_Func("SImm", {"SImm", "UImm", "F64Imm"}, func_arg, false, false, x);
        auto ext1 = SASS::TT_Ext(reg);
        auto ext2 = SASS::TT_Ext(reg);
        auto param1 = SASS::TT_Param({SASS::TT_OpAtAbs("Pg")}, reg, {ext1});
        auto param2 = SASS::TT_Param({SASS::TT_OpAtNegate("Pg")}, func, {ext2});
        auto param3 = SASS::TT_Param({SASS::TT_OpAtNot("pp")}, reg, {ext1});

        auto ops_vec = SASS::TOpsVec{ SASS::TT_OpAtNot("lol"), SASS::TT_OpAtAbs("lol"), SASS::TT_OpAtInvert("lol") };
        auto params1 = SASS::TParamVec {param1, param2};
        auto params2 = SASS::TParamVec {param3};
        auto list1 = SASS::TT_List(params1, SASS::TExtVec{ ext1 });
        auto list2 = SASS::TT_List(params2, SASS::TExtVec{ ext2 });

        auto attr = SASS::TT_AttrParam(ops_vec, reg, {list1, list2}, { ext1, ext2 }, false);

        auto xb = SASS::Pickle::dumps(attr.get_state());
        SASS::TT_AttrParam_State xs = SASS::Pickle::loads<SASS::TT_AttrParam_State>(xb);
        std::cout << attr.__str__() << std::endl;

        {
            SASS::TT_AttrParam* reca = reinterpret_cast<SASS::TT_AttrParam*>(new uint8_t[sizeof(SASS::TT_AttrParam)]);
            auto seq = std::make_index_sequence<SASS::tt_attrparam_state_size>{};
            SASS::TT_AttrParam::unpack(*reca, xb, seq);
            bool comp = (attr == *reca);
            delete reca;
        }
    }
    {
        auto alias = SASS::TT_Alias("hello", false);
        auto reg = SASS::TT_Reg("Register", x6, x);
        auto func = SASS::TT_Func("SImm", {"SImm", "UImm", "F64Imm"}, func_arg, false, false, x);
        auto ext1 = SASS::TT_Ext(reg);
        auto ext2 = SASS::TT_Ext(reg);
        auto param1 = SASS::TT_Param({SASS::TT_OpAtAbs("Pg")}, reg, {ext1});
        auto param2 = SASS::TT_Param({SASS::TT_OpAtNegate("Pg")}, func, {ext2});
        auto param3 = SASS::TT_Param({SASS::TT_OpAtNot("pp")}, reg, {ext1});

        auto ops_vec = SASS::TOpsVec{ SASS::TT_OpAtNot("lol"), SASS::TT_OpAtAbs("lol"), SASS::TT_OpAtInvert("lol") };
        auto params1 = SASS::TParamVec {param1, param2};
        auto params2 = SASS::TParamVec {param3};
        auto list1 = SASS::TT_List(params1, SASS::TExtVec{ ext1 });
        auto list2 = SASS::TT_List(params2, SASS::TExtVec{ ext2 });
        auto attr_param = SASS::TT_AttrParam(ops_vec, reg, {list1, list2}, { ext1, ext2 }, false);

        auto regular_param = SASS::TT_Param({SASS::TT_OpAtAbs("Pg")}, reg, {ext1});

        auto pred = SASS::TT_Pred(reg, SASS::TT_OpAtNot("lol"));

        auto opcode = SASS::TT_Opcode(alias, SASS::TT_ICode("010101", {0,1,2,3,4,5}, {010101}), {ext1, ext2});

        auto cash_param1 = SASS::TT_Param({}, SASS::TT_Reg("REQ", SASS::TT_Default(-1, false, {}), SASS::TT_Alias("req", false)), {});
        auto cash_param2 = SASS::TT_Param(
            {}, 
            SASS::TT_Func(
                "BITSET", 
                {"BITSET"}, 
                SASS::TT_FuncArg(5, false, false, 5, false, 0, false, 0),
                false, false,
                SASS::TT_Alias("req_sb_bitset", false)
            ),
            {});
        auto cash_param3 = SASS::TT_Param({}, SASS::TT_Reg("USCHED_INFO", SASS::TT_Default(-1, false, {}), SASS::TT_Alias("usched_info", false)), {});

        auto cash1 = SASS::TT_Cash({SASS::TT_OpCashAnd(), cash_param1, SASS::TT_OpCashAssign(), cash_param2});
        auto cash2 = SASS::TT_Cash({SASS::TT_OpCashQuestion(), cash_param3});

        auto tt_instruction = SASS::TT_Instruction("classeli", pred, opcode, {attr_param, list1, regular_param}, {cash1, cash2});

        auto xb = SASS::Pickle::dumps(tt_instruction.get_state());
        SASS::TT_Instruction_State xs = SASS::Pickle::loads<SASS::TT_Instruction_State>(xb);
        std::cout << tt_instruction.__str__() << std::endl;

        {
            SASS::TT_Instruction* reca = reinterpret_cast<SASS::TT_Instruction*>(new uint8_t[sizeof(SASS::TT_Instruction)]);
            SASS::TT_Instruction::unpack(*reca, xb, std::make_index_sequence<SASS::tt_instruction_state_size>{});
            bool comp = (tt_instruction == *reca);
            assert(comp == true);
            delete reca;
        }
    }

    // auto f2 = SASS::TT_Func("hellooooooooooooooooooooooooooooooo", "SImm", {}, SASS::TT_FuncArg(5, false, false, 5, false, 0, false, 0), false, false, SASS::TT_Alias(std::string("hwllo world")));
    // auto t = std::make_tuple<SASS::TT_Func>(std::move(f));
    
    return 0;
}