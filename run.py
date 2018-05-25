#!/usr/bin/env python
from __future__ import print_function

from chart import DrawingCore
import json
import re
import sys
import copy
from collections import OrderedDict
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', help="json file for plot", default="list.json")
    parser.add_argument('--mode', nargs=1, help="mode to run (draft/normal)", default="normal")
    return parser.parse_args()


def read_list_file():
    args = get_args()
    filename = args.file
    run_mode = args.mode[0]
    # print(run_mode)

    # try:
    f = open(filename)
    input_str = "\n".join(f.readlines())
    input_str = re.sub(r'\\\n', '', input_str)
    input_str = re.sub(r'//.*\n', '\n', input_str)
    lt = json.loads(input_str, object_pairs_hook=OrderedDict)
    f.close()

    if type(lt) is OrderedDict:
        print("%s dict detected. Advanced mode..." % filename)
        group = None

        if group:
            if group in lt:
                common = {}
                if "common" in lt[group]:
                    common = lt[group]["common"]
                for item in lt[group]["items"]:
                    nt = copy.copy(common)
                    nt.update(item)
                    DrawingCore(nt['file'], nt, run_mode)
            else:
                print("Group %s not found." % group)
        else:
            for k in lt:
                common = {}
                if "common" in lt[k]:
                    common = lt[k]["common"]
                for item in lt[k]["items"]:
                    nt = copy.copy(common)
                    nt.update(item)
                    DrawingCore(nt['file'], nt, run_mode)
    else:
        for item in lt:
            DrawingCore(item['file'], item, run_mode)
    # except IOError:
    #     print("%s not found." % filename)


if __name__ == '__main__':
    read_list_file()
