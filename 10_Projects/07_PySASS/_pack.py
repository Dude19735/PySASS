import os
import zipfile
import typing
import itertools as itt

if __name__ != '__main__':
    exit(0)

MOCK_RUN = False
if MOCK_RUN: PREF = '[MOCK] '
else: PREF = ''

location = os.path.dirname(os.path.realpath(__file__))
sms = [50,52,53,60,61,62,70,72,75,80,86,90,100,120]

with open('pack.history', 'w') as log_file:
    out = log_file.write

    # ========================================================================================================
    # Move instruction value pickles to zip
    sm_expr_vals = location + "/py_sass/sm_expr_vals"
    all_files = os.listdir(sm_expr_vals)
    all_pickles = [sm_expr_vals + "/" + i for i in all_files if (i.endswith('.pickle') and i.startswith('sm_'))]
    all_logs = [sm_expr_vals + "/" + i for i in all_files if (i.endswith('.log') and i.startswith('sm_'))]

    out(PREF + "Move all sass_expr_vals pickles to zip...\n")
    for sm in sms:
        sm_pickles_filenames = [i for i in all_pickles if i.find("sm_{0}".format(sm)) >= 0]
        sm_log_filenames = [i for i in all_logs if i.find("sm_{0}".format(sm)) >= 0]
        sm_zip_filename = sm_expr_vals + "/sm_{0}.all_expr_vals.zip".format(sm)

        if not sm_pickles_filenames: continue

        out(PREF + "...SM {0}: to {1}...\n".format(sm, sm_zip_filename))
        with zipfile.ZipFile(sm_zip_filename, 'r' if MOCK_RUN else 'w', zipfile.ZIP_DEFLATED) as zz:
            for fn in sm_pickles_filenames:
                out(PREF + "... ...SM {0}: {1} to {2}...\n".format(sm, fn, sm_zip_filename))
                if not MOCK_RUN: zz.write(fn, os.path.basename(fn))
            for fn in sm_log_filenames:
                out(PREF + "... ...SM {0}: {1} to {2}...\n".format(sm, fn, sm_zip_filename))
                if not MOCK_RUN: zz.write(fn, os.path.basename(fn))

        out(PREF + "...SM {0}: remove pickles...\n".format(sm))
        for fn in sm_pickles_filenames:
            out(PREF + "... ...SM {0}: remove {1}...\n".format(sm, fn))
            if not MOCK_RUN: os.remove(fn)
        for fn in sm_log_filenames:
            out(PREF + "... ...SM {0}: remove {1}...\n".format(sm, fn))
            if not MOCK_RUN: os.remove(fn)

        out(PREF + "...SM {0}: ok\n".format(sm))

    # ========================================================================================================
    # Move DocumentSASS to instr.zip
    document_sass_location = location + "/py_sass/DocumentSASS"
    all_files = os.listdir(document_sass_location)
    sm_files = dict()
    for sm in sms:
        sm_instruction_txt = [i for i in all_files if i.startswith("sm_{0}".format(sm)) and i.endswith('instructions.txt.in')]
        sm_latencies_txt = [i for i in all_files if i.startswith("sm_{0}".format(sm)) and i.endswith('latencies.txt.in')]
        sm_desc_json = [i for i in all_files if i.startswith("sm_{0}".format(sm)) and i.endswith('desc.json')]
        sm_non_sat_json = [i for i in all_files if i.startswith("sm_{0}".format(sm)) and i.endswith('non_sat.json')]
        sm_non_sat_rename = [i for i in all_files if i.startswith("sm_{0}".format(sm)) and i.endswith('non_sat.rename')]
        
        if not len(sm_instruction_txt) == 1: raise Exception('Should be only one file!')
        if not len(sm_latencies_txt) == 1: raise Exception('Should be only one file!')
        if not len(sm_desc_json) == 1: raise Exception('Should be only one file!')
        if not len(sm_non_sat_json) <= 1: raise Exception('Should be at most one file!')
        if not len(sm_non_sat_rename) <= 1: raise Exception('Should be at most one file!')
        
        sm_files[sm] = [
            document_sass_location + "/" + sm_instruction_txt[0],
            document_sass_location + "/" + sm_latencies_txt[0],
            document_sass_location + "/" + sm_desc_json[0]
        ]
        if sm_non_sat_json: sm_files[sm].append(document_sass_location + "/" + sm_non_sat_json[0])
        if sm_non_sat_rename: sm_files[sm].append(document_sass_location + "/" + sm_non_sat_rename[0])

    instr_zip_filename = document_sass_location + "/instr.zip"
    with zipfile.ZipFile(instr_zip_filename, 'r' if MOCK_RUN else 'w', zipfile.ZIP_DEFLATED) as zz:
        for sm,fs in sm_files.items():
            out(PREF + "SM {0}: move files to {1}...\n".format(sm, instr_zip_filename))
            for fn in fs:
                out(PREF + "...SM {0}: {1} to {2}...\n".format(sm, fn, instr_zip_filename))
                if not MOCK_RUN: zz.write(fn, os.path.basename(fn))
            out(PREF + "...SM {0}: ok\n".format(sm, instr_zip_filename))

        for sm,fs in sm_files.items():
            out(PREF + "SM {0}: remove files...\n".format(sm))
            for fn in fs:
                out(PREF + "...SM {0}: remove {1}...\n".format(sm, fn))
                if not MOCK_RUN: os.remove(fn)
            out(PREF + "...SM {0}: ok\n".format(sm, fs))
