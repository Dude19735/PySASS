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

if not 'CONST__VERBOSE' in locals(): CONST__VERBOSE = False
if not 'CONST__OUPUT_TO_FILE' in locals(): CONST__OUPUT_TO_FILE = False
if not 'CONST__TRUE' in locals(): CONST__TRUE = 'F'
if not 'CONST__SERVICE_RESPONSE_1' in locals(): CONST__SERVICE_RESPONSE_1 = '@+_+@'
if not 'CONST__SERVICE_RESPONSE_2' in locals(): CONST__SERVICE_RESPONSE_2 = '@#_#@'

if not 'CONST__ERROR_UNEXPECTED' in locals(): CONST__ERROR_UNEXPECTED = "Unexpected behaviour"
if not 'CONST__ERROR_ILLEGAL' in locals(): CONST__ERROR_ILLEGAL = "Illegal"
if not 'CONST__ERROR_NOT_IMPLEMENTED' in locals(): CONST__ERROR_NOT_IMPLEMENTED = "Not implemented"
if not 'CONST__ERROR_NOT_SUPPORTED' in locals(): CONST__ERROR_NOT_SUPPORTED = "Not supported"
if not 'CONST__ERROR_NOT_SUPPORTED' in locals(): CONST__CASH_TYPE_NOT_SUPPORTED = "Cash type is not supported"
if not 'CONST__ERROR_NOT_TESTED' in locals(): CONST__ERROR_NOT_TESTED = "Not tested"
if not 'CONST__ERROR_ONLY_70PP' in locals(): CONST__ERROR_ONLY_70PP = "Only supported from SM 70 and upwards!"
if not 'CONST__ERROR_ENCODEING_NOT_SUPPORTED' in locals(): CONST__ERROR_ENCODEING_NOT_SUPPORTED = "{0} is not encodable for instruction class {1}"

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

if not 'GLOBAL__CUR_SM' in locals(): GLOBAL__CUR_SM = 0
if not 'GLOBAL__SERVER_LOAD_ALL' in locals(): GLOBAL__SERVER_LOAD_ALL = True
