import os
import json
from .sm_sass import SM_SASS

"""
This script is used as workbench to create some config/whatever files. It is not meant to be "finished" at some point.
"""

def rename_sm(s):
    location = os.path.dirname(os.path.realpath(__file__)) + "/sm_expr_vals"
    doc_location = "/".join(location.split('/')[:-1]) + '/DocumentSASS'
    instr_p = location + "/sm_{0}.{1}.pickle"
    not_satisfiable_path = location + "/sm_{0}.xx.non_sat.{1}.log"
    not_satisfiable_ok_path = location + "/sm_{0}.ok.non_sat.{1}.log"

    # Check if we either have a pickle or a log that sais an instruction is not
    # satisfiable for every class in the system
    sass = SM_SASS(s)
    classes_ = sass.__sm.classes_dict

    # archive_location = os.path.dirname(os.path.realpath(__file__)) + "/sm_expr_vals/"
    # archive = archive_location + "sm_{0}.all_expr_vals.zip"
    # for ind,c in enumerate(classes_.keys()):
    #     p1 = os.path.exists(instr_p.format(s, c))
    #     p2 = os.path.exists(not_satisfiable_ok_path.format(s,c))
    #     if not (p1 or p2):
    #         # Check if we have a zip file. If not, we have to sample the CONDITIONS domains first
    #         if not os.path.exists(archive.format(s)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #         # Otherwise, unzip it
    #         with zipfile.ZipFile(archive.format(s), 'r') as zz:
    #             zz.extractall(archive_location)
    
    non_sat_files = []
    for c in classes_.keys():
        p1 = os.path.exists(instr_p.format(s, c))
        p2 = os.path.exists(not_satisfiable_ok_path.format(s,c))
        p3 = os.path.exists(not_satisfiable_path.format(s,c))
        if p1:
            pass
        elif p2:
            pass
            non_sat_files.append(c)
        elif p3:
            pass
            # non_sat_files.append((not_satisfiable_path.format(s,c), not_satisfiable_ok_path.format(s,c)))
        else:
            pass

    if non_sat_files:
        # This one serves for generation purposes.
        jj = json.dumps(non_sat_files, indent=4)
        with open(doc_location + "/sm_{0}_non_sat.json".format(s),'w') as f:
            f.write(jj)
            # f.write("AUTO GENERATED, DO NOT CHANGE!\n")
            # # f.write("\n".join(non_sat_files))
            # f.write("\n".join([os.path.split(i[0])[-1] + "|" + os.path.split(i[1])[-1] for i in non_sat_files]))
        
if __name__ == '__main__':

    sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90]
    # sms = [72]
    for sm in sms:
        rename_sm(sm)

