import os
import zipfile
from .sm_sass import SM_SASS

def main():
    """
    Use this one to generate all calculations.
    """

    location = os.path.dirname(os.path.realpath(__file__))
    doc_loc = location + "/DocumentSASS"
    instr_zip = doc_loc + "/instr.zip"

    with zipfile.ZipFile(instr_zip, 'r') as zz:
        zz.extractall(doc_loc)

    sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90, 100, 120]
    for sm in sms:
        sass = SM_SASS(sm, reparse=True, finalize=True, opcode_gen=True, lookup_gen=True, web_crawl=False)
    print("Installation calculations finished - Creating Lookup DB...")
    SM_SASS.create_lookup_db(sms)
    print("All Done!")

def main_finalize_only():
    """
    Use this one to only recalculate the 'finalize' step. This is much quicker and is enough for most on-the-fly changes.
    """
    location = os.path.dirname(os.path.realpath(__file__))
    doc_loc = location + "/DocumentSASS"
    instr_zip = doc_loc + "/instr.zip"

    with zipfile.ZipFile(instr_zip, 'r') as zz:
        zz.extractall(doc_loc)

    sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90, 100, 120]
    for sm in sms:
        sass = SM_SASS(sm, reparse=False, finalize=True, opcode_gen=False, lookup_gen=False, web_crawl=False)
    print("Installation calculations finished - Creating Lookup DB...")
    SM_SASS.create_lookup_db(sms)
    print("All Done!")
