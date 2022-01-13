#!/bin/bash

state=pearc22_possible_reviewers.json
if test -f "$state"; then
    rm -i ${state}
fi

./mergeminus.py --state ${state} --merge PEARC19_reviewers.csv
./mergeminus.py --state ${state} --merge PEARC20_reviewers.csv
./mergeminus.py --state ${state} --merge PEARC21_reviewers.csv
./mergeminus.py --state ${state} --minus PEARC22_reviewer_signups.csv
