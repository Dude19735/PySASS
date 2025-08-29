#pragma once
#include <functional>
#include <set>
#include <string>
#include <string_view>
#include <format>
#include <cmath>
#include <numeric>
#include <iostream>
#include <utility>
#include <type_traits>
#include <tuple>
#include <algorithm>
#include <unordered_map>

#include "SASS_Func.hpp"
#include "Utils.hpp"
#include "SASS_Bits.hpp"
#include "SASS_Range.hpp"
#include "Pickle.hpp"
#include "TT_Terms.hpp"

namespace SASS {

    using TOperandType = std::variant<TT_Param, TT_List>;
    using TOperandStateType = std::variant<TT_Param_State, TT_List_State>;
    constexpr size_t operand_type_size = std::variant_size_v<TOperandType>;
    static_assert(std::variant_size_v<TOperandType> == std::variant_size_v<TOperandStateType>);

    using TEvalType = std::variant<TT_Reg, TT_Func, TT_AtOp, TT_ICode>;
    using TEvalStateType = std::variant<TT_Reg_State, TT_Func_State, TT_AtOp_State, TT_ICode_State>;
    constexpr size_t eval_type_size = std::variant_size_v<TEvalType>;
    static_assert(std::variant_size_v<TEvalType> == std::variant_size_v<TEvalStateType>);

    using TOperandVec = std::vector<TOperandType>;
    using TOperandStateVec = std::vector<TOperandStateType>;
    using TCashVec = std::vector<TT_Cash>;
    using TCashStateVec = std::vector<TT_Cash_State>;
    using TEvalDict = std::unordered_map<std::string, TEvalType>;
    using TEvalStateDict = std::unordered_map<std::string, TEvalStateType>;

    using TT_Instruction_State_0 = std::tuple<std::string, TT_Pred_State, TT_Opcode_State, TOperandStateVec, TCashStateVec, TEvalStateDict>;
    using TT_Instruction_State = std::variant<TT_Instruction_State_0>;
    constexpr size_t tt_instruction_state_size = std::tuple_size<TT_Instruction_State_0>::value;
    class TT_Instruction : public Picklable<TT_Instruction, TT_Instruction_State, tt_instruction_state_size> {
        std::string _class_name;
        TT_Pred _pred;
        TT_Opcode _opcode;
        TOperandVec _regs;
        TCashVec _cashs;
        TEvalDict _eval;
        
    public:
        TT_Instruction(const std::string& class_name, const TT_Pred& pred, const TT_Opcode& opcode, const TOperandVec& regs, const TCashVec& cashs, const TEvalDict eval) noexcept
          : _class_name(class_name), _pred(pred), _opcode(opcode), _regs(regs), _cashs(cashs), _eval(eval) {}
        TT_Instruction(const std::string& class_name, const TT_Pred_State& pred, const TT_Opcode_State& opcode, const TOperandStateVec& regs, const TCashStateVec& cashs, const TEvalStateDict eval) noexcept
          : _class_name(class_name), _pred(TT_Pred::muh(pred)), _opcode(TT_Opcode::muh(opcode)), _regs(TT_Instruction::muv_vec_h<TOperandType, TOperandStateType, operand_type_size>(regs)), _cashs(TT_Cash::from_state_vec(cashs)), _eval(TT_Instruction::muv_umap_h<std::string, TEvalType, TEvalStateType, eval_type_size>(eval)) {}
        TT_Instruction(const TT_Instruction& other) noexcept 
          : _class_name(other._class_name), _pred(other._pred), _opcode(other._opcode), _regs(other._regs), _cashs(other._cashs), _eval(other._eval) {}
        TT_Instruction(TT_Instruction&& other) noexcept 
          : _class_name(std::move(other._class_name)), _pred(std::move(other._pred)), _opcode(std::move(other._opcode)), _regs(std::move(other._regs)), _cashs(std::move(other._cashs)), _eval(std::move(other._eval)) {}
        TT_Instruction operator=(const TT_Instruction& other) noexcept { if(this == &other) return *this; _class_name = other._class_name; _pred = other._pred; _opcode = other._opcode; _regs = other._regs; _cashs = other._cashs; _eval = other._eval; return *this; }
        TT_Instruction operator=(TT_Instruction&& other) noexcept { if(this == &other) return *this; _class_name = std::move(other._class_name); _pred = std::move(other._pred); _opcode = std::move(other._opcode); _regs = std::move(other._regs); _cashs = std::move(other._cashs); _eval = std::move(other._eval); return *this; }
        bool operator==(const TT_Instruction& other) const { if(this == &other) return true; return (_class_name.compare(other._class_name) == 0) && (_pred == other._pred) && (_opcode == other._opcode) && (_regs == other._regs) && (_cashs == other._cashs) && (_eval == other._eval); }

        const TT_Instruction_State get_state(TT_Instruction* selfp=nullptr) const override { 
            return std::make_tuple(_class_name, _pred.get_state(), _opcode.get_state(), 
                TT_Instruction::mpv_vec_h<TOperandStateType, TOperandType, operand_type_size>(_regs), TT_Cash::to_state_vec(_cashs), TT_Instruction::mpv_umap_h<std::string, TEvalStateType, TEvalType, eval_type_size>(_eval)); }
        const std::string __str__() const noexcept {
            std::stringstream res;
            res << "FORMAT";
            if(!_pred.is_none()){
                res << " PREDICATE " << _pred.__str__();
            }
            res << " " << _opcode.__str__() << std::endl;
            size_t s = _regs.size();
            for(size_t i=0; i<s; ++i){
                if(i > 0) res << "   ,";
                else res << "    ";
                res << std::visit([&](const auto& r) { return r.__str__(); }, _regs.at(i)) << std::endl;
            }
            s = _cashs.size();
            for(size_t i=0; i<s; ++i){
                res << _cashs.at(i).__str__();
                if(i < s-1) res << std::endl;
            }
            return res.str();
        }

        TT_Pred pred() const noexcept { return _pred; }
        TT_Opcode opcode() const noexcept { return _opcode; }
        TOperandVec regs() const noexcept { return _regs; }
        TCashVec cashs() const noexcept { return _cashs; }
        TEvalDict eval() const noexcept { return _eval; }
        
    };
}