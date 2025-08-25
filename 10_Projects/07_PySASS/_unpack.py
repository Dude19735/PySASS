import os
import zipfile
import typing
import itertools as itt

if __name__ != '__main__':
    exit(0)

location = os.path.dirname(os.path.realpath(__file__))
sms = [50,52,53,60,61,62,70,72,75,80,86,90,100,120]

UNPACK_INSTRUCTIONS = False
UNPACK_DOCUMENTSASS = True

# ========================================================================================================
# Unpack instruction zips
# sm_expr_vals = location + "/py_sass/sm_expr_vals"
# for sm in sms:
#     pickle_zip = sm_expr_vals + "/sm_{0}.all_expr_vals.zip".format(sm)
#     with zipfile.ZipFile(pickle_zip, 'r') as zz:
#         zz.extractall(sm_expr_vals)

# ========================================================================================================
# Move DocumentSASS to instr.zip
doc_loc = location + "/py_sass/DocumentSASS"
instr_zip = doc_loc + "/instr.zip"

with zipfile.ZipFile(instr_zip, 'r') as zz:
    zz.extractall(doc_loc)

    