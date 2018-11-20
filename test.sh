#!/bin/bash


HVite -C configs/config -H build/hmm12/macros -H build/hmm12/hmmdefs -S build/train.scp -l '*' -i build/rec.mlf -w build/sample.dfa -p 0.0 -s 5.0 sample.dict build/triphones1

HResults build/rec.mlf build/words.mlf 
