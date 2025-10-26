import time
import random

"""
while there are tokens to be read:
    read a token
    if the token is:
    - a number:
        put it into the output queue
    - a function:
        push it onto the operator stack 
    - an operator o1:
        while (
            there is an operator o2 at the top of the operator stack which is not a left parenthesis, 
            and (o2 has greater precedence than o1 or (o1 and o2 have the same precedence and o1 is left-associative))
        ):
            pop o2 from the operator stack into the output queue
        push o1 onto the operator stack
    - a ",":
        while the operator at the top of the operator stack is not a left parenthesis:
             pop the operator from the operator stack into the output queue
    - a left parenthesis (i.e. "("):
        push it onto the operator stack
    - a right parenthesis (i.e. ")"):
        while the operator at the top of the operator stack is not a left parenthesis:
            {assert the operator stack is not empty}
            /* If the stack runs out without finding a left parenthesis, then there are mismatched parentheses. */
            pop the operator from the operator stack into the output queue
        {assert there is a left parenthesis at the top of the operator stack}
        pop the left parenthesis from the operator stack and discard it
        if there is a function token at the top of the operator stack, then:
            pop the function from the operator stack into the output queue
/* After the while loop, pop the remaining items from the operator stack into the output queue. */
while there are tokens on the operator stack:
    /* If the operator token on the top of the stack is a parenthesis, then there are mismatched parentheses. */
    {assert the operator on top of the stack is not a (left) parenthesis}
    pop the operator from the operator stack onto the output queue
"""

if not 'CONST__OP_COLOR' in locals(): CONST__OP_COLOR='light_grey'
if not 'CONST__OP_ATTRS' in locals(): CONST__OP_ATTRS=[]
if not 'CONST__OPCODE_COLOR' in locals(): CONST__OPCODE_COLOR='red'
if not 'CONST__OPCODE_ATTRS' in locals(): CONST__OPCODE_ATTRS=['bold']
if not 'CONST__PRED_COLOR' in locals(): CONST__PRED_COLOR='blue'
if not 'CONST__PRED_ATTRS' in locals(): CONST__PRED_ATTRS=[]
if not 'CONST__REG_DST_COLOR' in locals(): CONST__REG_DST_COLOR='magenta'
if not 'CONST__REG_DST_ATTRS' in locals(): CONST__REG_DST_ATTRS=['bold']
if not 'CONST__REG_SRC_COLOR' in locals(): CONST__REG_SRC_COLOR='red'
if not 'CONST__REG_SRC_ATTRS' in locals(): CONST__REG_SRC_ATTRS=['bold']
if not 'CONST__EXT_COLOR' in locals(): CONST__EXT_COLOR='cyan'
if not 'CONST__EXT_ATTRS' in locals(): CONST__EXT_ATTRS=[]
if not 'CONST__ATTR_COLOR' in locals(): CONST__ATTR_COLOR='magenta'
if not 'CONST__ATTR_ATTRS' in locals(): CONST__ATTR_ATTRS=[]
if not 'CONST__CONST_COLOR' in locals(): CONST__CONST_COLOR='yellow'
if not 'CONST__CONST_ATTRS' in locals(): CONST__CONST_ATTRS=[]
if not 'CONST__CASH_COLOR' in locals(): CONST__CASH_COLOR='green'
if not 'CONST__CASH_ATTRS' in locals(): CONST__CASH_ATTRS=[]
if not 'CONST__NUM_COLOR' in locals(): CONST__NUM_COLOR='blue'
if not 'CONST__NUM_ATTRS' in locals(): CONST__NUM_ATTRS=[]
if not 'CONST__PARAM_COLOR' in locals(): CONST__PARAM_COLOR='light_red'
if not 'CONST__PARAM_ATTRS' in locals(): CONST__PARAM_ATTRS=[]
if not 'CONST__MISC_COLOR' in locals(): CONST__MISC_COLOR='white'
if not 'CONST__MISC_ATTRS' in locals(): CONST__MISC_ATTRS=[]

if not 'EXPR_OP_ASSOCIATIV_GROUP_NONE' in locals(): EXPR_OP_ASSOCIATIV_GROUP_NONE = 'X'
if not 'EXPR_OP_PRECEDENCE_NR_NONE' in locals(): EXPR_OP_PRECEDENCE_NR_NONE = -1
if not 'EXPR_OP_ASSOCIATIV_GROUP_COMMA' in locals(): EXPR_OP_ASSOCIATIV_GROUP_COMMA = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_COMMA' in locals(): EXPR_OP_PRECEDENCE_NR_COMMA = 10000
if not 'EXPR_OP_ASSOCIATIV_GROUP_OPERAND' in locals(): EXPR_OP_ASSOCIATIV_GROUP_OPERAND = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_OPERAND' in locals(): EXPR_OP_PRECEDENCE_NR_OPERAND = 1000
if not 'EXPR_OP_ASSOCIATIV_GROUP_FUNCTION' in locals(): EXPR_OP_ASSOCIATIV_GROUP_FUNCTION = 'R'
if not 'EXPR_OP_PRECEDENCE_NR_FUNCTION' in locals(): EXPR_OP_PRECEDENCE_NR_FUNCTION = 0
if not 'EXPR_OP_ASSOCIATIV_GROUP_CTRL' in locals(): EXPR_OP_ASSOCIATIV_GROUP_CTRL = 'R'
if not 'EXPR_OP_PRECEDENCE_NR_CTRL' in locals(): EXPR_OP_PRECEDENCE_NR_CTRL = 100
if not 'EXPR_OP_ASSOCIATIV_GROUP_0' in locals(): EXPR_OP_ASSOCIATIV_GROUP_0 = 'R'
if not 'EXPR_OP_PRECEDENCE_NR_0' in locals(): EXPR_OP_PRECEDENCE_NR_0 = 0
if not 'EXPR_OP_ASSOCIATIV_GROUP_1' in locals(): EXPR_OP_ASSOCIATIV_GROUP_1 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_1' in locals(): EXPR_OP_PRECEDENCE_NR_1 = 1
if not 'EXPR_OP_ASSOCIATIV_GROUP_2' in locals(): EXPR_OP_ASSOCIATIV_GROUP_2 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_2' in locals(): EXPR_OP_PRECEDENCE_NR_2 = 2
if not 'EXPR_OP_ASSOCIATIV_GROUP_3' in locals(): EXPR_OP_ASSOCIATIV_GROUP_3 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_3' in locals(): EXPR_OP_PRECEDENCE_NR_3 = 3
if not 'EXPR_OP_ASSOCIATIV_GROUP_4' in locals(): EXPR_OP_ASSOCIATIV_GROUP_4 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_4' in locals(): EXPR_OP_PRECEDENCE_NR_4 = 4
if not 'EXPR_OP_ASSOCIATIV_GROUP_5' in locals(): EXPR_OP_ASSOCIATIV_GROUP_5 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_5' in locals(): EXPR_OP_PRECEDENCE_NR_5 = 5
if not 'EXPR_OP_ASSOCIATIV_GROUP_6' in locals(): EXPR_OP_ASSOCIATIV_GROUP_6 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_6' in locals(): EXPR_OP_PRECEDENCE_NR_6 = 6
if not 'EXPR_OP_ASSOCIATIV_GROUP_7' in locals(): EXPR_OP_ASSOCIATIV_GROUP_7 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_7' in locals(): EXPR_OP_PRECEDENCE_NR_7 = 7
if not 'EXPR_OP_ASSOCIATIV_GROUP_8' in locals(): EXPR_OP_ASSOCIATIV_GROUP_8 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_8' in locals(): EXPR_OP_PRECEDENCE_NR_8 = 8
if not 'EXPR_OP_ASSOCIATIV_GROUP_9' in locals(): EXPR_OP_ASSOCIATIV_GROUP_9 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_9' in locals(): EXPR_OP_PRECEDENCE_NR_9 = 9
if not 'EXPR_OP_ASSOCIATIV_GROUP_10' in locals(): EXPR_OP_ASSOCIATIV_GROUP_10 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_10' in locals(): EXPR_OP_PRECEDENCE_NR_10 = 10
if not 'EXPR_OP_ASSOCIATIV_GROUP_11' in locals(): EXPR_OP_ASSOCIATIV_GROUP_11 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_11' in locals(): EXPR_OP_PRECEDENCE_NR_11 = 11
if not 'EXPR_OP_ASSOCIATIV_GROUP_12' in locals(): EXPR_OP_ASSOCIATIV_GROUP_12 = 'R'
if not 'EXPR_OP_PRECEDENCE_NR_12' in locals(): EXPR_OP_PRECEDENCE_NR_12 = 12
if not 'EXPR_OP_ASSOCIATIV_GROUP_13' in locals(): EXPR_OP_ASSOCIATIV_GROUP_13 = 'L'
if not 'EXPR_OP_PRECEDENCE_NR_13' in locals(): EXPR_OP_PRECEDENCE_NR_13 = 13

if not 'RANDOM__SEED_1' in locals(): RANDOM__SEED_1 = int("".join([str(time.time_ns()), str(random.randint(1000,9999))]))
if not 'RANDOM__SEED_2' in locals(): RANDOM__SEED_2 = int("".join([str(time.time_ns()), str(random.randint(1000,9999))]))
if not 'RANDOM__SEED_3' in locals(): RANDOM__SEED_3 = int("".join([str(time.time_ns()), str(random.randint(1000,9999))]))
if not 'RANDOM__SEED_4' in locals(): RANDOM__SEED_4 = int("".join([str(time.time_ns()), str(random.randint(1000,9999))]))

if not 'CONST__VERBOSE' in locals(): CONST__VERBOSE = False
if not 'CONST__OUPUT_TO_FILE' in locals(): CONST__OUTPUT_TO_FILE = False
if not 'CONST__TRUE' in locals(): CONST__TRUE = 'F'
if not 'CONST__SERVICE_RESPONSE_1' in locals(): CONST__SERVICE_RESPONSE_1 = '@+_+@'
if not 'CONST__SERVICE_RESPONSE_2' in locals(): CONST__SERVICE_RESPONSE_2 = '@#_#@'

if not 'CONST__ERROR_UNEXPECTED' in locals(): CONST__ERROR_UNEXPECTED = "Unexpected behaviour"
if not 'CONST__ERROR_ILLEGAL' in locals(): CONST__ERROR_ILLEGAL = "Illegal"
if not 'CONST__ERROR_NOT_IMPLEMENTED' in locals(): CONST__ERROR_NOT_IMPLEMENTED = "Not implemented"
if not 'CONST__ERROR_NOT_TESTED' in locals(): CONST__ERROR_NOT_TESTED = "Not tested"
if not 'CONST__ERROR_DEPRECATED' in locals(): CONST__ERROR_DEPRECATED = "Attempted to run deprecated code!"

if not 'CONST_NAME__SKIP' in locals(): CONST_NAME__SKIP = 'SKIP'
if not 'CONST_NAME__FORMAT' in locals(): CONST_NAME__FORMAT = 'FORMAT'
if not 'CONST_NAME__FORMAT_ALIAS' in locals(): CONST_NAME__FORMAT_ALIAS = 'FORMAT_ALIAS'
if not 'CONST_NAME__OPCODES' in locals(): CONST_NAME__OPCODES = 'OPCODES'
if not 'CONST_NAME__REMAP' in locals(): CONST_NAME__REMAP = 'REMAP'
if not 'CONST_NAME__IS_ALTERNATE' in locals(): CONST_NAME__IS_ALTERNATE = 'IS_ALTERNATE'
if not 'CONST_NAME__CONDITION' in locals(): CONST_NAME__CONDITION = 'CONDITION'
if not 'CONST_NAME__CONDITIONS' in locals(): CONST_NAME__CONDITIONS = 'CONDITIONS'
if not 'CONST_NAME__PROPERTIES' in locals(): CONST_NAME__PROPERTIES = 'PROPERTIES'
if not 'CONST_NAME__PREDICATES' in locals(): CONST_NAME__PREDICATES = 'PREDICATES'
if not 'CONST_NAME__ENCODING' in locals(): CONST_NAME__ENCODING = 'ENCODING'

if not 'OPERATION SETS' in locals(): CONST_NAME__OPERATION_SETS = 'OPERATION SETS'
if not 'ALL_CONNECTORS' in locals(): CONST_NAME__ALL_CONNECTORS = 'ALL_CONNECTORS'
if not 'CONNECTOR CONDITIONS' in locals(): CONST_NAME__CONNECTOR_CONDITIONS = 'CONNECTOR CONDITIONS'
if not 'CONNECTOR SETS' in locals(): CONST_NAME__CONNECTOR_SETS = 'CONNECTOR SETS'
if not 'TABLE_TRUE' in locals(): CONST_NAME__TABLE_TRUE = 'TABLE_TRUE'
if not 'TABLE_OUTPUT' in locals(): CONST_NAME__TABLE_OUTPUT = 'TABLE_OUTPUT'
if not 'TABLE_ANTI' in locals(): CONST_NAME__TABLE_ANTI = 'TABLE_ANTI'
if not 'PIPELINE RESOUCE' in locals(): CONST_NAME__PIPELINE_RESOURCE = 'PIPELINE RESOURCE'
if not 'OPERATION PIPELINE RESOURCES' in locals(): CONST_NAME__OPERATION_PIPELINE_RESOURCES = 'OPERATION PIPELINE RESOURCES'

if not 'CONST_INT__SKIP' in locals(): CONST_INT__SKIP = 0
if not 'CONST_INT__FORMAT' in locals(): CONST_INT__FORMAT = 1
if not 'CONST_INT__FORMAT_ALIAS' in locals(): CONST_INT__FORMAT_ALIAS = 2
if not 'CONST_INT__OPCODES' in locals(): CONST_INT__OPCODES = 3
if not 'CONST_INT__REMAP' in locals(): CONST_INT__REMAP = 4
if not 'CONST_INT__IS_ALTERNATE' in locals(): CONST_INT__IS_ALTERNATE = 5
if not 'CONST_INT__CONDITION' in locals(): CONST_INT__CONDITION = 6
if not 'CONST_INT__CONDITIONS' in locals(): CONST_INT__CONDITIONS = 7
if not 'CONST_INT__PROPERTIES' in locals(): CONST_INT__PROPERTIES = 8
if not 'CONST_INT__PREDICATES' in locals(): CONST_INT__PREDICATES = 9
if not 'CONST_INT__ENCODING' in locals(): CONST_INT__ENCODING = 10

if not 'CONST_LU__MAIN' in locals(): CONST_LU__MAIN = 'main'
if not 'CONST_LU__ALT' in locals(): CONST_LU__ALT = 'alt'
if not 'CONST_LU__LOOKUP' in locals(): CONST_LU__LOOKUP = 'lookup'
if not 'CONST_LU__LOOKUP_FIXED_IND' in locals(): CONST_LU__LOOKUP_FIXED_IND = 'fixed_ind'
if not 'CONST_LU__LOOKUP_FIXED_VAL' in locals(): CONST_LU__LOOKUP_FIXED_VAL = 'fixed_val'
if not 'CONST_LU__LOOKUP_NZ_IND' in locals(): CONST_LU__LOOKUP_NZ_IND = 'nz_ind'
if not 'CONST_LU__LOOKUP_REQEN_VAL' in locals(): CONST_LU__LOOKUP_REQEN_VAL = 'req'
if not 'CONST_LU__DESC' in locals(): CONST_LU__DESC = 'desc'

if not 'TEST__MOCK_INSTRUCTIONS' in locals(): TEST__MOCK_INSTRUCTIONS = False
if not 'TEST__MOCK_INSTRUCTIONS_COUNT' in locals(): 
    TEST__MOCK_INSTRUCTIONS_COUNT = 3 # MUST BE A MULTIPLE OF 3!!!
    if not TEST__MOCK_INSTRUCTIONS_COUNT%3==0: raise Exception("Must be a multiple of 3!")
if not 'TEST__SWITCH_1' in locals(): TEST__SWITCH_1 = False

if not 'GLOBAL__USED_RAM_SAMPLES' in locals(): GLOBAL__USED_RAM_SAMPLES = [] 

if not 'GLOBAL__ALL_DEFAULTS' in locals(): GLOBAL__ALL_DEFAULTS = [] 
if not 'GLOBAL__ALL_REMAINDERS' in locals(): GLOBAL__ALL_REMAINDERS = [] 
if not 'GLOBAL__ALL_NON_REGS' in locals(): GLOBAL__ALL_NON_REGS = [] 
if not 'GLOBAL__ALL_FUNCTIONS' in locals(): GLOBAL__ALL_FUNCTIONS = []
if not 'GLOBAL__ALL_ACCESSORS' in locals(): GLOBAL__ALL_ACCESSORS = []
if not 'GLOBAL__ALL_FAILED_INSTR_BITS' in locals(): GLOBAL__ALL_FAILED_INSTR_BITS = {}
if not 'GLOBAL__ALL_PREDICATE_VALS' in locals(): GLOBAL__ALL_PREDICATE_VALS = set()
if not 'GLOBAL__ALL_CONDITIONS' in locals(): GLOBAL__ALL_CONDITIONS = dict()

if not 'GLOBAL__CUR_SM' in locals(): GLOBAL__CUR_SM = 0
if not 'GLOBAL__EXPRESSIONS_COLLECT_STATS' in locals(): GLOBAL__EXPRESSIONS_COLLECT_STATS = False
if not 'GLOBAL__EXPRESSIONS' in locals(): GLOBAL__EXPRESSIONS = dict()
if not 'GLOBAL__EXPRESSIONS_OLD_NEW_COR' in locals(): GLOBAL__EXPRESSIONS_OLD_NEW_COR = dict()
if not 'GLOBAL__EXPRESSIONS_VAR_COUNT' in locals(): GLOBAL__EXPRESSIONS_VAR_COUNT = dict()
if not 'GLOBAL__EXPRESSIONS_EXAMPLE' in locals(): GLOBAL__EXPRESSIONS_EXAMPLE = dict()
if not 'GLOBAL__EXPRESSIONS_FIRST_SM' in locals(): GLOBAL__EXPRESSIONS_FIRST_SM = dict()
if not 'GLOBAL__EXPRESSIONS_LAST_SM' in locals(): GLOBAL__EXPRESSIONS_LAST_SM = dict()
if not 'GLOBAL__EXPRESSIONS_FIRST_INSTR' in locals(): GLOBAL__EXPRESSIONS_FIRST_INSTR = dict()
if not 'GLOBAL__EXPRESSIONS_ALL_RANGE_INSTR' in locals(): GLOBAL__EXPRESSIONS_ALL_RANGE_INSTR = dict()
if not 'GLOBAL__LARGE_FUNC_EXPRESSIONS' in locals(): GLOBAL__LARGE_FUNC_EXPRESSIONS = dict()
if not 'GLOBAL__LARGE_FUNC_EXPRESSIONS_OLD_NEW_COR' in locals(): GLOBAL__LARGE_FUNC_EXPRESSIONS_OLD_NEW_COR = dict()
if not 'GLOBAL__EXPRESSIONS_TESTED' in locals(): GLOBAL__EXPRESSIONS_TESTED = set()

if not 'GLOBAL__CASH_EXPR' in locals(): GLOBAL__CASH_EXPR = dict()
if not 'GLOBAL__CASH_EXPR_EXTRA' in locals(): GLOBAL__CASH_EXPR_EXTRA = dict()

if not 'GLOBAL__SERVER_LOAD_ALL' in locals(): GLOBAL__SERVER_LOAD_ALL = True

if not 'CACHE__SM' in locals(): CACHE__SM = {}

if not 'SWITCH__USE_TT_EXT' in locals(): SWITCH__USE_TT_EXT = True
if not 'SWITCH__USE_OP_EXT' in locals(): SWITCH__USE_OP_EXT = False
if not 'SWITCH__USE_PROPS_EXT' in locals(): SWITCH__USE_PROPS_EXT = False

if not 'SM_LATENCY__ORDERED_ZERO' in locals(): SM_LATENCY__ORDERED_ZERO = "ORDERED_ZERO"
if not 'SM_LATENCY__ORDERED_ZERO_VAL' in locals(): SM_LATENCY__ORDERED_ZERO_VAL = 0
if not "SM_LATENCY__TABLE_OUTPUT" in locals(): SM_LATENCY__TABLE_OUTPUT = 'TABLE_OUTPUT'
if not "SM_LATENCY__TABLE_TRUE" in locals(): SM_LATENCY__TABLE_TRUE = 'TABLE_TRUE'
if not "SM_LATENCY__TABLE_ANTI" in locals(): SM_LATENCY__TABLE_ANTI = 'TABLE_ANTI'

if not 'SM_LATENCY__SM_50_TO_62_CONNECTOR_CONDITIONS' in locals(): 
    SM_LATENCY__SM_50_TO_62_CONNECTOR_CONDITIONS = {
    'RaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'RbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'RcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'RdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'Rd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'VTG' : '(vtg == 0) || 0',
    'VTG_PRED' : '(VTG) && ((vtgmode == 1 || vtgmode == 2) || 0)',
    'CC_NON_CONST' : '((CCTest != 0) && (CCTest != 15)) || ((fcomp != 0) && (fcomp != 15))',
    'CC_CSM' : '((CCTest >= 0x18) && (CCTest <= 0x1d)) || ((fcomp >= 0x18) && (fcomp <= 0x1d))',
    'CC_READ' : '(DOES_READ_CC == 1)'
}

if not 'SM_LATENCY__SM_70_TO_72_CONNECTOR_CONDITIONS' in locals(): 
    SM_LATENCY__SM_70_TO_72_CONNECTOR_CONDITIONS = {
    'RaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'RbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'RcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'RdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'Rd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'VTG_PRED' : '((vtgmode == 2 || vtgmode == 3) || 0)'
}

if not 'SM_LATENCY__SM_75_CONNECTOR_CONDITIONS' in locals(): 
    SM_LATENCY__SM_75_CONNECTOR_CONDITIONS = {
    'RaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'RbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'RcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'RdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'Rd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'URaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'URbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'URcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'URdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'URd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'VTG_PRED' : '((vtgmode == 2 || vtgmode == 3) || 0)'
}

if not 'SM_LATENCY__SM_80_TO_86_CONNECTOR_CONDITIONS' in locals(): 
    SM_LATENCY__SM_80_TO_86_CONNECTOR_CONDITIONS = {
    'RaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'RbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'RcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'ReRange' : '(((((ISRC_E_SIZE) >= (1)) ? (ISRC_E_SIZE) : (1)) - 1) >> 5) + 1',
    'RdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'Rd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'URaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'URbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'URcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'UReRange' : '(((((ISRC_E_SIZE) >= (1)) ? (ISRC_E_SIZE) : (1)) - 1) >> 5) + 1',
    'URdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'URd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'VTG_PRED' : '((vtgmode == 2 || vtgmode == 3) || 0)'
}
    
if not 'SM_LATENCY__SM_90_CONNECTOR_CONDITIONS' in locals(): 
    SM_LATENCY__SM_90_CONNECTOR_CONDITIONS = {
    'RaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'RbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'RcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'ReRange' : '(((((ISRC_E_SIZE) >= (1)) ? (ISRC_E_SIZE) : (1)) - 1) >> 5) + 1',
    'RdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'Rd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'URaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'URbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'URcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'UReRange' : '(((((ISRC_E_SIZE) >= (1)) ? (ISRC_E_SIZE) : (1)) - 1) >> 5) + 1',
    'URdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'URd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'MODE_ARV_WAIT' : '((mode == 0 || mode == 1) || 0)',
    'MODE_DEPBAR' : '((mode == 2) || 0)',
    'GSB_GSB0' : '((gsb != 7) || 0)',
    'VTG_PRED' : '((vtgmode == 2 || vtgmode == 3) || 0)'
}
    
if not 'SM_LATENCY__SM_100_CONNECTOR_CONDITIONS' in locals(): 
    SM_LATENCY__SM_100_CONNECTOR_CONDITIONS = {
    'RaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'RbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'Rb2Range' : '(((((ISRC_B2_SIZE) >= (1)) ? (ISRC_B2_SIZE) : (1))- 1) >> 5) + 1',
    'RcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'ReRange' : '(((((ISRC_E_SIZE) >= (1)) ? (ISRC_E_SIZE) : (1)) - 1) >> 5) + 1',
    'RdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'Rd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'URaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'URbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'URcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'UReRange' : '(((((ISRC_E_SIZE) >= (1)) ? (ISRC_E_SIZE) : (1)) - 1) >> 5) + 1',
    'URhRange' : '(((((ISRC_H_SIZE) >= (1)) ? (ISRC_H_SIZE) : (1)) - 1) >> 5) + 1',
    'URiRange' : '(((((ISRC_I_SIZE) >= (1)) ? (ISRC_I_SIZE) : (1)) - 1) >> 5) + 1',
    'URdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'URd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1'
}

if not 'SM_LATENCY__SM_120_CONNECTOR_CONDITIONS' in locals(): 
    SM_LATENCY__SM_120_CONNECTOR_CONDITIONS = {
    'RaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'RbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'Rb2Range' : '(((((ISRC_B2_SIZE) >= (1)) ? (ISRC_B2_SIZE) : (1))- 1) >> 5) + 1',
    'RcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'ReRange' : '(((((ISRC_E_SIZE) >= (1)) ? (ISRC_E_SIZE) : (1)) - 1) >> 5) + 1',
    'RhRange' : '(((((ISRC_H_SIZE) >= (1)) ? (ISRC_H_SIZE) : (1)) - 1) >> 5) + 1',
    'RdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'Rd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1',
    'URaRange' : '(((((ISRC_A_SIZE) >= (1)) ? (ISRC_A_SIZE) : (1)) - 1) >> 5) + 1',
    'URbRange' : '(((((ISRC_B_SIZE) >= (1)) ? (ISRC_B_SIZE) : (1)) - 1) >> 5) + 1',
    'URcRange' : '(((((ISRC_C_SIZE) >= (1)) ? (ISRC_C_SIZE) : (1)) - 1) >> 5) + 1',
    'UReRange' : '(((((ISRC_E_SIZE) >= (1)) ? (ISRC_E_SIZE) : (1)) - 1) >> 5) + 1',
    'URhRange' : '(((((ISRC_H_SIZE) >= (1)) ? (ISRC_H_SIZE) : (1)) - 1) >> 5) + 1',
    'URiRange' : '(((((ISRC_I_SIZE) >= (1)) ? (ISRC_I_SIZE) : (1)) - 1) >> 5) + 1',
    'URdRange' : '(((((IDEST_SIZE) >= (1)) ? (IDEST_SIZE) : (1)) - 1) >> 5) + 1',
    'URd2Range' : '(((((IDEST2_SIZE) >= (1)) ? (IDEST2_SIZE) : (1)) - 1) >> 5) + 1'
}
    
if not 'SM_LATENCY__CONNECTOR_CONDITIONS' in locals(): 
    SM_LATENCY__CONNECTOR_CONDITIONS = {
    50:SM_LATENCY__SM_50_TO_62_CONNECTOR_CONDITIONS,  # type: ignore
    52:SM_LATENCY__SM_50_TO_62_CONNECTOR_CONDITIONS,  # type: ignore
    53:SM_LATENCY__SM_50_TO_62_CONNECTOR_CONDITIONS, # type: ignore
    60:SM_LATENCY__SM_50_TO_62_CONNECTOR_CONDITIONS, # type: ignore
    61:SM_LATENCY__SM_50_TO_62_CONNECTOR_CONDITIONS, # type: ignore
    62:SM_LATENCY__SM_50_TO_62_CONNECTOR_CONDITIONS, # type: ignore
    70:SM_LATENCY__SM_70_TO_72_CONNECTOR_CONDITIONS, # type: ignore
    72:SM_LATENCY__SM_70_TO_72_CONNECTOR_CONDITIONS, # type: ignore
    75:SM_LATENCY__SM_75_CONNECTOR_CONDITIONS, # type: ignore
    80:SM_LATENCY__SM_80_TO_86_CONNECTOR_CONDITIONS, # type: ignore
    86:SM_LATENCY__SM_80_TO_86_CONNECTOR_CONDITIONS, # type: ignore
    90:SM_LATENCY__SM_90_CONNECTOR_CONDITIONS, # type: ignore
    100: SM_LATENCY__SM_100_CONNECTOR_CONDITIONS, # type: ignore
    120: SM_LATENCY__SM_120_CONNECTOR_CONDITIONS  # type: ignore
}

if not 'SM_PREDICATE_CACHE' in locals(): SM_PREDICATE_CACHE = {} 
