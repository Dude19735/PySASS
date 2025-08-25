import os
import asyncio
import zipfile
import typing
import _config as sp
from sass_expression_domain_parse import SASS_Expression_Domain_Parse
from sass_expression_domain_calc_conditions import SASS_Expression_Domain_Calc_Conditions
from sass_expression_domain_encoding import SASS_Expr_Domain_Encoding

"""
This script generates everything
"""

class SASS_Gen_All:
    TEMPLATE = """
import time
import datetime
import psutil
import _config as sp
from sass_expression_domain_parse import SASS_Expression_Domain_Parse
from sass_expression_domain_calc_conditions import SASS_Expression_Domain_Calc_Conditions
from sass_expression_domain_encoding import SASS_Expr_Domain_Encoding

###############################################################################
# AUTO-GENEREATED FILE: DO NOT CHANGE!!!
# source /home/lol/.venvs/standard/bin/activate && python3 {filename}
###############################################################################

sp.CONST__OUPUT_TO_FILE = True
sp.GLOBAL__EXPRESSIONS_COLLECT_STATS = True
sp.CONFIG__GEN_LARGE = {CONFIG__GEN_LARGE}
sp.CONFIG__GEN_SMALL = {CONFIG__GEN_SMALL}

if not ((sp.CONFIG__GEN_LARGE == True) or (sp.CONFIG__GEN_SMALL == True)):
    raise Exception("Must choose between generating the large encoding LZ4s (test instruction encode/decode) or the small ones (benchmarker)!")

if (sp.CONFIG__GEN_LARGE == True) and (sp.CONFIG__GEN_SMALL == True):
    raise Exception("Must choose between generating the large encoding LZ4s (test instruction encode/decode) or the small ones (benchmarker)!")


reparse = {reparse}
finalize = {finalize}
opcode_gen = {opcode_gen}
lookup_gen = {lookup_gen}
web_crawl = {web_crawl}
override = {override}
test = {test}
stop_on_exception = {stop_on_exception}
skip_tested = {skip_tested}
single_class = {single_class}
single_class_name = "{single_class_name}"
load_enc = {load_enc}
enc_dom_test = {enc_dom_test}
enc_dom_tester = "{enc_dom_tester}"
encoding_single_class = {encoding_single_class}
encoding_single_class_name = "{encoding_single_class_name}"
sm = {sm}

sp.GLOBAL__USED_RAM_SAMPLES.append(psutil.virtual_memory().used)

t_start = time.time()
{generate_statistics}SASS_Expression_Domain_Parse.statistics([sm], reparse, finalize, opcode_gen, lookup_gen, web_crawl)
{generate_domains}SASS_Expression_Domain_Calc_Conditions.gen([sm], override, test, stop_on_exception, skip_tested, single_class, single_class_name)
{consolidate_domains}SASS_Expr_Domain_Encoding.consolidate([sm], load_enc, enc_dom_test, enc_dom_tester, encoding_single_class, encoding_single_class_name)
t_end = time.time()

max_mem = max(sp.GLOBAL__USED_RAM_SAMPLES) / 10.0**9
print("====================================================================================================")
print("All finished at " + datetime.datetime.now().strftime('%d.%m.%Y - %H:%M') + " after " + str(round(t_end - t_start, 2)) + " seconds with approximate max memory usage " + str(max_mem) + "GB")
"""
    @staticmethod
    async def run_sms(scripts:list):
        procs = []
        files:typing.List[typing.TextIO] = []
        for script_name in scripts:
            f = open(script_name + ".log", 'w')
            proc = await asyncio.create_subprocess_exec('python3', '{script_name}'.format(script_name=script_name), stdout=f, )
            procs.append(proc)
            files.append(f)

        await asyncio.gather(*[p.communicate() for p in procs])

        for f in files: f.close()

    @staticmethod
    def gen_all(sms:list, 
                generate_statistics:bool, reparse:bool, finalize:bool, opcode_gen:bool, lookup_gen:bool, web_crawl:bool, 
                generate_domains:bool, override:bool, test:bool, stop_on_exception:bool, skip_tested:bool, single_class:bool, single_class_name:str,
                consolidate_domains:bool, load_enc:bool, enc_dom_test:bool, enc_dom_tester:str, encoding_single_class:bool, encoding_single_class_name:str,
                CONFIG__GEN_LARGE:bool, CONFIG__GEN_SMALL:bool):
        if not isinstance(sms, list): raise Exception(sp.CONST__ERROR_ILLEGAL)

        if not isinstance(generate_statistics, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(reparse, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(finalize, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(opcode_gen, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(lookup_gen, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(web_crawl, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)

        if not isinstance(generate_domains, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(override, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(test, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(stop_on_exception, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(skip_tested, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(single_class, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if single_class and not (isinstance(single_class_name, str) and len(single_class_name) > 0): raise Exception(sp.CONST__ERROR_ILLEGAL)

        if not isinstance(consolidate_domains, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(load_enc, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_dom_test, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_dom_tester, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if(enc_dom_test and enc_dom_tester==""): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(encoding_single_class, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if encoding_single_class and not (isinstance(encoding_single_class_name, str) and len(encoding_single_class_name) > 0): raise Exception(sp.CONST__ERROR_ILLEGAL)

        if not isinstance(CONFIG__GEN_LARGE, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(CONFIG__GEN_SMALL, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)

        location = os.path.dirname(os.path.realpath(__file__))
        archive = location + "/DocumentSASS/instr.zip"
        archive_extract_location = location + "/DocumentSASS"
        path = location + '/DocumentSASS/sm_'
        name_s = '_instructions.txt'
        name = name_s + '.in'

        # for sm in sms:
        #     instructions_txt = path + str(sm) + name
        #     if not os.path.exists(instructions_txt):
        #         if not os.path.exists(archive): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        #         with zipfile.ZipFile(archive, 'r') as zz:
        #             zz.extractall(archive_extract_location)

        scripts = []
        for sm in sms:
            script_name = os.path.dirname(os.path.realpath(__file__)) + "/__auto_generated_sm_{0}_gen.py".format(sm)
            with open(script_name, 'w') as f:
                script = SASS_Gen_All.TEMPLATE.format(
                    filename=os.path.dirname(os.path.realpath(__file__)) + "/__auto_generated_sm_{0}_gen.py".format(sm),
                    sm=sm,
                    generate_statistics = '' if generate_statistics else '#',
                      reparse=reparse, 
                      finalize=finalize, 
                      opcode_gen=opcode_gen, 
                      lookup_gen=lookup_gen,
                      web_crawl=web_crawl, 
                    generate_domains = '' if generate_domains else '#',
                      override=override, 
                      test=test, 
                      stop_on_exception=stop_on_exception, 
                      skip_tested=skip_tested,
                      single_class=single_class,
                      single_class_name=single_class_name,
                    consolidate_domains = '' if consolidate_domains else '#',
                      load_enc=load_enc,
                      enc_dom_test=enc_dom_test,
                      enc_dom_tester=enc_dom_tester.format(sm),
                      encoding_single_class=encoding_single_class,
                      encoding_single_class_name=encoding_single_class_name,
                    CONFIG__GEN_LARGE=CONFIG__GEN_LARGE,
                    CONFIG__GEN_SMALL=CONFIG__GEN_SMALL)
                print("Create " + script_name)
                f.write(script)
            scripts.append(script_name)

        return scripts
    
    @staticmethod
    def run_all(scripts:list, delete_after:bool = True):
        print("============================================================================================================")
        print("SM gen started...")
        print("============================================================================================================")
        asyncio.run(SASS_Gen_All.run_sms(scripts))
        print()
        if not delete_after:
            print("Manually delete the following scripts")
            for sc in scripts: print(" - " + sc)
            print("============================================================================================================")
        else:
            SASS_Gen_All.delete_all(scripts)

    @staticmethod
    def delete_all(scripts:list):
        print("Delete gen scripts:")
        for script_name in scripts:
            print(" - {0}".format(script_name))
            os.remove(script_name)
        print("============================================================================================================")

# safeguard
if not __name__ == '__main__':
    exit(0)
#################################################################################
# read sass_expression_domain.readme for more information
#################################################################################

# NOTE: generating all SMs at the same time requires more than 16GB or ram!!

# sms=[50, 52, 53, 60, 61, 62]  # requires approx 2GB of ram  (on top of usual usage)
# sms=[70, 72, 75]              # requires approx 6GB of ram  (on top of usual usage)
# sms=[80, 86]                  # requires approx 13GB of ram (on top of usual usage)
# sms=[90]                      # requires approx 10GB of ram (on top of usual usage)   
#                                 --------------------------------------------------
#                                 total: about 32 GB of ram but not all at once since
#                                        the lower SMs are much faster than the higher
#                                        SMs. Running all at once on a PC with 32GB of
#                                        ram works.

# Setting this to true will create the full fledged LZ4s that can be used to test the encoder/decoder
CONFIG__GEN_LARGE = False
# Setting this to true will generate LZ4s that can be used for benchmarking variable latency instructions
#  - all cash bits are set to 0x7 or 0, depending on what they are => no variability here makes the LZ4s smaller
#  - registers 0 to 29 are reserved for SASS boilerplate for the benchmarking sauce, 255 can be used as well, since it's constant 0
#  - registers 30 to 50 and 255 are used for variability in the instructions, 255 is included since it's constant 0
CONFIG__GEN_SMALL = True

if not ((CONFIG__GEN_LARGE == True) or (CONFIG__GEN_SMALL == True)):
    raise Exception("Must choose between generating the large encoding LZ4s (test instruction encode/decode) or the small ones (benchmarker)!")

if (CONFIG__GEN_LARGE == True) and (CONFIG__GEN_SMALL == True):
    raise Exception("Must choose between generating the large encoding LZ4s (test instruction encode/decode) or the small ones (benchmarker)!")


# sms = [50, 52, 53, 60, 61, 62, 70, 72, 100]
# sms = [75, 80, 86]
sms = [90, 120]

# Statistics
# ==========
# toggle SASS_Expression_Domain_Parse.statistics
generate_statistics = False
# Reparse all sm_xx_instruction.txt.
# Usually, setting this to False is fine unless anything that has to do with the parser has been changed.
reparse = False
# Apply finalize step (translate TT_Term to TT_Predicate etc...).
# Usually, setting this to False is fine unless anything that has to do with the TT.. objects has been changed.
finalize = True
# Dig out opcodes from finalized objects and translate to binary pattern if necessary.
# Usually, if either reparse or finalize is not False, set this to True. Otherwise, False is fine.
opcode_gen = False
# Generate lookup table for parsing instructions.
# Generally, if finalize==True, set this one to True as well.
lookup_gen = False
# Download instruction descriptions from Nvidia's SASS website and recreate sm_xx_instr_desc.json
# NOTE: all json files should be in instr.zip. Nvidia changes their website every now and then. Redoing the web_crawl=True step
# may require adjusting [sm_cu.py/__web_scrape] method
# Leave this False unless a new architecture that has never been parsed before ever by anyone has to be parsed. And even if this
# is the case, parse only the new architecture with this set to True.
web_crawl = False

# Valid alias value sets
# ======================
# Set this to true to re-generate all pickles in sm_expr_vals.
# The zip files are not extracted by this one but by the consolidate_domains step.
# To just extract the zip files, use consolidate_domains=True
generate_domains = True
# Override pickle for instruction class if it exists.
# Set this to True to override every single class. If only some missing instruction classes have to be generated, set it to False.
# All instruction classes without any pickle will be generated in both cases.
override = False
# Test at least the first value set for each CONDITIONS expression pattern.
# It is recomended to leave this to True at least the first time everyting is generated.
test = True
# Throw exception if there is a problem.
# It is recomended to only set this to True if _sass_expression_domain_cals.py has to be tested.
# All relevant problems will generate logs.
stop_on_exception = True
# only test the first occurrence for each CONDITIONS expression pattern
# NOTE: if not True, it may easily take a day to complete!!
# Probably best to not bother with skip_tested=False.
skip_tested = True
# If this one is true, only the domains for this particular class will be recalculated.
# This is mainly a debug functionality to save time. If 'single_class = True', then
# 'single_class_name' must be the name of an existinc class. The user is responsible to choose an
# existing name.
single_class = False
single_class_name = 'ATOM'

# Consolidate alias value sets
# ============================
consolidate_domains = True
# If we have an sm_XX_domains.json inside of instr.zip, we can use this one to just
# load the ENCODINGS stage values => set load_enc = True
# If we don't, we have to run the complete consolidation process. NOTE that this can
# take a while for all SMs >= 70 due to their complex texture instructions.
load_enc = False
# Test json loader: calc domains, store them, reload and compare the reloaded result
# with the calculated one.
# NOTE: this doesn't make any sense if 'load_end_json = True' at the same time.
enc_dom_test = False
enc_dom_tester = os.path.dirname(os.path.realpath(__file__)) + "/DocumentSASS/sm_{0}_domains.old.lz4"
encoding_single_class = single_class
encoding_single_class_name = single_class_name

scripts = SASS_Gen_All.gen_all(
    sms=sms, 
    generate_statistics=generate_statistics, 
      reparse=reparse, 
      finalize=finalize, 
      opcode_gen=opcode_gen, 
      lookup_gen=lookup_gen,
      web_crawl=web_crawl, 
    override=override, 
      generate_domains=generate_domains, 
      test=test, 
      stop_on_exception=stop_on_exception, 
      skip_tested=skip_tested,
      single_class=single_class,
      single_class_name=single_class_name,
    consolidate_domains=consolidate_domains,
      load_enc=load_enc,
      enc_dom_test=enc_dom_test,
      enc_dom_tester=enc_dom_tester,
      encoding_single_class=encoding_single_class,
      encoding_single_class_name=encoding_single_class_name,
    CONFIG__GEN_LARGE=CONFIG__GEN_LARGE,
    CONFIG__GEN_SMALL=CONFIG__GEN_SMALL)
SASS_Gen_All.run_all(scripts, delete_after=True)
