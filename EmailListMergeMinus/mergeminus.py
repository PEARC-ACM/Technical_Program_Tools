#!/usr/bin/env python3
import argparse
import csv
import json
import sys
import pdb

class LowerDictReader(csv.DictReader):
    # This class overrides the csv.fieldnames property, which converts all fieldnames without leading and trailing spaces and to lower case.
    @property
    def fieldnames(self):
        return [field.strip().lower() for field in csv.DictReader.fieldnames.fget(self)]

    def next(self):
        return InsensitiveDict(csv.DictReader.next(self))

parser = argparse.ArgumentParser(description='Merge or minus emails and their names from a json state file')
parser.add_argument('--state', action='store', help='The json file to merge/minus/print email addresses into/from')
parser.add_argument('--merge', action='store', help='The CSV file to merge email addresses from')
parser.add_argument('--minus', action='store', help='The CSV file to minus email addresses of')
parser.add_argument('--print', action='store_true', help='Print the state file')
args=parser.parse_args()
if not args.merge and not args.minus and not args.print:
    print('Must specify either a merge or minus file, or the print option')
    sys.exit(1)

#pdb.set_trace()

if args.merge:
    print('** Merge ==> {}'.format(args.merge))
elif args.minus:
    print('** Minus ==> {}'.format(args.minus))

# Load state
try:
    with open(args.state, 'r') as state_file:
        state_raw = state_file.read()
    state_dict = json.loads(state_raw)
except FileNotFoundError:
    print('Initializing state file={}'.format(args.state))
    state_dict = {}
except Exception as e:
    print('Exception loading state={}'.format(e))
    sys.exit(1)

if args.print:
    for key in state_dict:
        print('"{}" <{}>'.format(state_dict[key], key))
    sys.exit(0)
    
# Load input
input = {}
inputcount = 0
try:
    with open(args.merge or args.minus, 'r') as input_file:
        input_reader = LowerDictReader(input_file, delimiter=',', quotechar='"')
        for row in input_reader:
            inputcount += 1
            if not row.get('email'):
                print('Skipping missing input email in row {}'.format(inputcount))
            else:
                input[row.get('email')] = row.get('last name') + ', ' + row.get('first name')
except Exception as e:
    print('Exception processing input={}'.format(e))
    sys.exit(1)

rows_done = 0
rows_add = 0
rows_del = 0

rows_initial = len(state_dict)
for row in input:
    rows_done += 1
    if args.merge:
        if row not in state_dict:
            rows_add += 1
        state_dict[row] = input[row]
    else: # args.minus
        if row in state_dict:
            rows_del += 1
            state_dict.pop(row, None)
rows_final = len(state_dict)

try:
    with open(args.state, 'w+') as state_file:
        json.dump(state_dict, state_file, indent=4, sort_keys=True)
except Exception as e:
    print('Exception saving state={}'.format(e))
    sys.exit(1)

print('Rows start={}, processed={}, added={}, deleted={}, end={}'.format(rows_initial, rows_done, rows_add, rows_del, rows_final))
