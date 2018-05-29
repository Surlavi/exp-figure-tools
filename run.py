#!/usr/bin/env python
from __future__ import print_function
from matplotlib import __version__ as mpl_version

from chart import DrawingCore
import json
import re
import subprocess
import copy
from collections import OrderedDict
import argparse


def env_check(args):
    # check mpl_version
    t = mpl_version.split('.')
    if int(t[0]) < 2:
        print("matplotlib >= 2.0.0 needed. Now version " + mpl_version + ".")
        exit()

    # check tex environment
    if args.mode[0] == 'normal':
        try:
            subprocess.check_output('tex --version')
        except subprocess.CalledProcessError:
            print("Tex not found. Install tex or run in draft mode: `python run.py <json_file> --mode=draft`")
            exit()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', help="json file for plot", default="list.json")
    parser.add_argument('--mode', nargs=1, help="mode to run (draft/normal)", default="normal")
    return parser.parse_args()


def read_list_file():
    args = get_args()
    env_check(args)
    filename = args.file
    run_mode = args.mode[0]

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


if __name__ == '__main__':
    read_list_file()
