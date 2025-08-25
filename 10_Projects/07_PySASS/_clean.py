import os
import zipfile
import typing
import itertools as itt

if __name__ != '__main__':
    exit(0)

MOCK_RUN = False
if MOCK_RUN: PREF = '[MOCK] '
else: PREF = ''

def get_X_files(locations:list, comp:typing.Callable):
    ff = list(itt.chain.from_iterable([loc + "/" + i for i in os.listdir(loc) if comp(i)] for loc in locations))
    return ff

def remove_X_files(out, files:list, start_stmt:str):
    run_stmt=PREF + "...remove {0}..."
    end_stmt=PREF + "...ok\n"

    out(start_stmt + "\n")
    for f in files:
        out(run_stmt.format(f) + "\n")
        if not MOCK_RUN: os.remove(f)
    out(end_stmt + "\n")

location = os.path.dirname(os.path.realpath(__file__))
sms = [50,52,53,60,61,62,70,72,75,80,86,90,100,120]

with open('clean.history', 'w') as log_file:
    out = log_file.write

    # ========================================================================================================
    # Clean all .autogen., __auto_generated, .out and .log files
    main_location = location
    sass_location = main_location + "/py_sass"
    document_sass_location = location + "/py_sass/DocumentSASS"
    # temp_location = location + "/temp"
    
    locations = [
        main_location, 
        sass_location,
        document_sass_location
    ]
    all__auto_generated_files = get_X_files(locations, lambda x: x.startswith("__auto_generated_"))
    all_autogen_files = get_X_files(locations, lambda x: x.find(".autogen.") >= 0)
    all_out_files = get_X_files(locations, lambda x: x.endswith(".out"))
    all_log_files = get_X_files(locations, lambda x: x.endswith(".log"))
    all_pickle_files = get_X_files(locations, lambda x: x.endswith(".pickle"))
    # all_temp_files = get_X_files([temp_location], lambda x: True)

    remove_X_files(out, all__auto_generated_files, start_stmt=PREF + "Remove [__auto_generated_*] files...")
    remove_X_files(out, all_autogen_files, start_stmt=PREF + "Remove [*.autogen.*] files...")
    remove_X_files(out, all_out_files, start_stmt=PREF + "Remove [.out] files...")
    remove_X_files(out, all_log_files, start_stmt=PREF + "Remove [*.log] files...")
    remove_X_files(out, all_pickle_files, start_stmt=PREF + "Remove [*.pickle] files...")
    # remove_X_files(out, all_temp_files, start_stmt=PREF + "Remove [temp] files...")
