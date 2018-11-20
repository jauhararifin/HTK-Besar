#!/bin/bash

rm -rf build
mkdir build

echo "Create DFA from grammar file"
HParse sample.grammar build/sample.dfa

echo "Create wlist from prompts.txt"
scripts/prompts2wlist prompts.txt build/wlist
echo "SENT-END" >> build/wlist
echo "SENT-START" >> build/wlist
sort build/wlist > build/wlist.temp
mv build/wlist.temp build/wlist

echo "Create dict and monophones1 & monophones0"
HDMan -A -D -T 1 -m -w build/wlist -g scripts/global.ded -n build/monophones1 -i -l build/dlog build/dict sample.dict
cat build/dlog
sed -n '/sp/!p' build/monophones1 > build/monophones0

echo "Create mlf file from prompts"
scripts/prompts2mlf build/words.mlf prompts.txt

echo "Create mlf contains phoneme from words.mlf"
HLEd -A -D -T 1 -l '*' -d build/dict -i build/phones0.mlf scripts/mkphones0.led build/words.mlf
HLEd -A -D -T 1 -l '*' -d build/dict -i build/phones1.mlf scripts/mkphones1.led build/words.mlf 

echo "Extract mfcc feature"
for file in *.wav; do
	name=$(basename $file .wav)
	echo "./$file" "build/mfc/$name.mfc" >> build/codetrain.scp
done
mkdir -p build/mfc
HCopy -A -D -T 1 -C configs/wav_config -S build/codetrain.scp

echo "Train HMM0"
for file in *.wav; do
	name=$(basename $file .wav)
	echo "build/mfc/$name.mfc" >> build/train.scp
done
mkdir -p build/hmm0
HCompV -A -D -T 1 -C configs/config -f 0.01 -m -S build/train.scp -M build/hmm0 configs/proto

echo "Create hmmdefs"
cp build/monophones0 build/hmm0/hmmdefs.temp
for phone in `cat build/hmm0/hmmdefs.temp`; do
	echo "~h $phone" >> build/hmm0/hmmdefs
	tail -n +5 build/hmm0/proto >> build/hmm0/hmmdefs
done
echo "" >> build/hmm0/hmmdefs
rm build/hmm0/hmmdefs.temp

head -n 3 build/hmm0/proto > build/hmm0/macros
cat build/hmm0/vFloors >> build/hmm0/macros

echo "Reestimate hmm"
mkdir build/hmm1
HERest -A -D -T 1 -C configs/config -I build/phones0.mlf -t 250.0 150.0 1000.0 \
	-S build/train.scp -H build/hmm0/macros -H build/hmm0/hmmdefs -M build/hmm1 build/monophones0

mkdir build/hmm2
HERest -A -D -T 1 -C configs/config -I build/phones0.mlf -t 250.0 150.0 1000.0 \
	-S build/train.scp -H build/hmm1/macros -H build/hmm1/hmmdefs -M build/hmm2 build/monophones0

mkdir build/hmm3
HERest -A -D -T 1 -C configs/config -I build/phones0.mlf -t 250.0 150.0 1000.0 \
	-S build/train.scp -H build/hmm2/macros -H build/hmm2/hmmdefs -M build/hmm3 build/monophones0

cp -r build/hmm3 build/hmm4
tail -n 18 build/hmm4/hmmdefs | head -n 5 > /tmp/tempfile
echo "~h \"sp\"" >> build/hmm4/hmmdefs
echo "<BEGINHMM>" >> build/hmm4/hmmdefs
echo "<NUMSTATES> 3" >> build/hmm4/hmmdefs
echo "<STATE> 2" >> build/hmm4/hmmdefs
cat /tmp/tempfile >> build/hmm4/hmmdefs
echo "<TRANSP> 3" >> build/hmm4/hmmdefs
echo "0.0 1.0 0.0" >> build/hmm4/hmmdefs
echo "0.0 0.9 0.1" >> build/hmm4/hmmdefs
echo "0.0 0.0 0.0" >> build/hmm4/hmmdefs
echo "<ENDHMM>" >> build/hmm4/hmmdefs
echo "" >> build/hmm4/hmmdefs
rm /tmp/tempfile

mkdir build/hmm5
HHEd -A -D -T 1 -H build/hmm4/macros -H build/hmm4/hmmdefs -M build/hmm5 configs/sil.hed build/monophones1

mkdir build/hmm6
HERest -A -D -T 1 -C configs/config  -I build/phones1.mlf -t 250.0 150.0 3000.0 \
	-S build/train.scp -H build/hmm5/macros -H  build/hmm5/hmmdefs -M build/hmm6 build/monophones1

mkdir build/hmm7
HERest -A -D -T 1 -C configs/config  -I build/phones1.mlf -t 250.0 150.0 3000.0 \
	-S build/train.scp -H build/hmm6/macros -H  build/hmm6/hmmdefs -M build/hmm7 build/monophones1

HVite -A -D -T 1 -l '*' -o SWT -b SENT-END -C configs/config -H build/hmm7/macros \
	-H build/hmm7/hmmdefs -i build/aligned.mlf -m -t 250.0 150.0 1000.0 \
	-y lab -a -I build/words.mlf -S build/train.scp build/dict build/monophones1 > build/HVite_log

mkdir build/hmm8
HERest -A -D -T 1 -C configs/config -I build/aligned.mlf -t 250.0 150.0 3000.0 \
	-S build/train.scp -H build/hmm7/macros -H build/hmm7/hmmdefs -M build/hmm8 build/monophones1 

mkdir build/hmm9
HERest -A -D -T 1 -C configs/config -I build/aligned.mlf -t 250.0 150.0 3000.0 \
	-S build/train.scp -H build/hmm8/macros -H build/hmm8/hmmdefs -M build/hmm9 build/monophones1

HLEd -A -D -T 1 -n build/triphones1 -l '*' -i build/wintri.mlf scripts/mktri.led build/aligned.mlf

scripts/maketrihed build/monophones1 build/triphones1
mv mktri.hed build/mktri.hed

mkdir build/hmm10
HHEd -A -D -T 1 -H build/hmm9/macros -H build/hmm9/hmmdefs -M build/hmm10 build/mktri.hed build/monophones1 

mkdir build/hmm11
HERest -A -D -T 1 -C configs/config -I build/wintri.mlf -t 250.0 150.0 3000.0 \
	-S build/train.scp -H build/hmm10/macros -H build/hmm10/hmmdefs -M build/hmm11 build/triphones1 

mkdir build/hmm12
HERest -A -D -T 1 -C configs/config -I build/wintri.mlf -t 250.0 150.0 3000.0 \
	-s build/stats -S build/train.scp -H build/hmm11/macros -H build/hmm11/hmmdefs -M build/hmm12 build/triphones1

HDMan -A -D -T 1 -b sp -n build/fulllist0 -g scripts/maketriphones.ded -l build/flog build/dict-tri sample.dict

cat build/fulllist0 >> build/fulllist
cat build/monophones0 >> build/fulllist
sort -u build/fulllist > /tmp/tempfile
cp /tmp/tempfile build/fulllist


