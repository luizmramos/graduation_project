#!/usr/bin/env python

import json
import sys


def main(args):
    with open(args[1], 'r') as f:
        data = json.loads(f.read())
    for example in data:
        if not example['links']:
            continue

    import pdb; pdb.set_trace()

if __name__ == '__main__':
    exit(main(sys.argv))
