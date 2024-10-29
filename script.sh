#!/bin/bash

for i in {1..20}
do
    python3 main.py < input/input-$i.txt > output/output-$i.txt
done
