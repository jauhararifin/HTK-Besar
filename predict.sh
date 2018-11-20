#!/bin/bash

filename=$1
echo $filename /tmp/mfc_feature > /tmp/feature_extraction.scp
HCopy -A -D -T 1 -C configs/wav_config -S /tmp/feature_extraction.scp > /dev/null

echo /tmp/mfc_feature > /tmp/predict_feature.scp

HVite -C configs/config -H build/hmm12/macros -H build/hmm12/hmmdefs \
	-S /tmp/predict_feature.scp -l '*' -i /tmp/prediction.mlf -w build/sample.dfa \
	-p 0.0 -s 5.0 sample.dict build/triphones1 > /dev/null

first=true
tail -n +3 /tmp/prediction.mlf | while read line; do
	if [[ "$line" =~ ^[0-9]+\ [0-9]+\ ([a-zA-Z0-9]+)\ -?\.*[0-9]+.?[0-9]* ]]; then
		if [ $first = false ]; then
			printf " "
		fi
		printf ${BASH_REMATCH[1]}
		first=false
	fi
done
printf "\n"

rm /tmp/mfc_feature
rm /tmp/feature_extraction.scp
rm /tmp/predict_feature.scp
rm /tmp/prediction.mlf
