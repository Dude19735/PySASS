from .sm_sass import SM_SASS
from .sm_latency import SM_Latency

if __name__ != '__main__':
    exit(0)

"""
This one is part of the latencies.txt parser.
"""

sms = [50, 52, 53, 60, 61, 62]
sms = [70, 72, 75, 80, 86, 90, 100, 120]
sms = [90, 100, 120]
for sm_nr in sms:
    sass = SM_SASS(sm_nr)

    matches = []
    for instr_class in sass.__sm.classes_dict.values():
        matches.append(sass.__latencies.match(instr_class))

    SM_Latency.matches_to_file('sm_{0}_lat_test_nz.autogen.log'.format(sm_nr), matches, lambda x: x > 0, lambda x: x == 2)
    SM_Latency.matches_to_file('sm_{0}_lat_test_z.autogen.log'.format(sm_nr), matches, lambda x: x == 0, lambda x: True)
