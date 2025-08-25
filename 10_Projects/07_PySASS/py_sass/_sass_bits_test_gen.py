import os
import itertools as itt
from .sm_sass import SM_SASS

if __name__ == '__main__':
    sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90]
    single_class = True
    codes = []
    for sm in sms:
        sass:SM_SASS
        sass = SM_SASS(sm)

        xx = [(k,v.ENCODING) for k,v in sass.sm.classes_dict.items()]
        dd = {
            'ev': sass.sm.details.FUNIT.encoding_width, # type: ignore
            'ind': list(itt.chain.from_iterable((cn, *list(itt.chain.from_iterable([ee for ee in e['code_ind']] for e in en))) for cn, en in xx))
        }
        codes.append(dd)
    
    fp = os.path.split(os.path.realpath(__file__))[0] + "/__auto_generated_sass_bits_test_gen.txt"
    with open(fp, 'w') as f:
        line_ind = 0
        for ind,s in enumerate(codes):
            print(ind, len(codes), end='')
            f.write(str(line_ind + len(s['ind'])+2) + "\n")
            line_ind += 1
            f.write(str(s['ev']) + "\n")
            line_ind += 1
            f.write("\n".join([str(i) for i in s['ind']]) + "\n")
            line_ind += len(s['ind'])
            print("finished")
    pass
