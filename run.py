#!/usr/bin/env python
from chart import DrawingCore
import json
import re
import sys
import copy
from collections import OrderedDict


def read_list_file(filename):
    # try:
    f = open(filename)
    input_str = "\n".join(f.readlines())
    input_str = re.sub(r'\\\n', '', input_str)
    input_str = re.sub(r'//.*\n', '\n', input_str)
    lt = json.loads(input_str, object_pairs_hook=OrderedDict)
    f.close()

    if type(lt) is OrderedDict:
        print "%s dict detected. Advanced mode..." % filename
        group = None
        if len(sys.argv) >= 3:
            group = sys.argv[2]
        if group:
            if group in lt:
                common = {}
                if "common" in lt[group]:
                    common = lt[group]["common"]
                for item in lt[group]["items"]:
                    nt = copy.copy(common)
                    nt.update(item)
                    DrawingCore(nt['file'], nt)
            else:
                print "Group %s not found." % group
        else:
            for k in lt:
                common = {}
                if "common" in lt[k]:
                    common = lt[k]["common"]
                for item in lt[k]["items"]:
                    nt = copy.copy(common)
                    nt.update(item)
                    DrawingCore(nt['file'], nt)
    else:
        for item in lt:
            DrawingCore(item['file'], item)
    # except IOError:
    #     print("%s not found." % filename)


if __name__ == '__main__':
    conf_file = 'list.json'
    if len(sys.argv) >= 2:
        conf_file = sys.argv[1]

    read_list_file(conf_file)
