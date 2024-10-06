#!/bin/bash -eu

#---------------------------------VARIABLES--------------------------------#
#export PATH=$PATH:/root/pairtoolsenv/bin
outpath=/root/tmpfs
prefix=$SRX_ID
resolution=$RESOLUTION

exec > /root/tmpfs/C10.stdout.txt 2>&1
#--------------------------------------------------------------------------#


#------------------------------PREPARE-CONTAINER---------------------------#
echo "Preparing container ..."

# copy over python script
aws s3 cp s3://maasslab/scr/leiden_CD.py $outpath/
# copy over cooler output
aws s3 cp s3://maasslab/$prefix/cd.$resolution.iced.sorted.txt $outpath/

echo "Done"
#--------------------------------------------------------------------------#


#----------------------------------SCRIPT----------------------------------#
cd $outpath

echo "# Initiate Leiden Community Detection ..."
python3 $outpath/leiden_CD.py $outpath cd.$resolution.iced.sorted.txt $resolution \
	&& { echo "Done" ; } \
	|| { echo "leiden_CD.py failed with error... exiting" ; }
#--------------------------------------------------------------------------#


#---------------------------------SAVING-----------------------------------#
echo "# Saving output"
aws s3 cp $outpath/leiden_CD_$resolution.txt s3://maasslab/$prefix/
echo "Done"
#--------------------------------------------------------------------------#




#------------------------------SAVING-stdout-------------------------------#
aws s3 sync --quiet s3://maasslab/$prefix/ $outpath/ --exclude "*" --include "C*.stdout.txt"

file_pre=$outpath/$prefix.preprocessing.stdout.txt

echo -e "#--------------------------------------------------# \n#    CONTAINER 1:                                  # \n#--------------------------------------------------# \n" > $file_pre
cat $outpath/C1.stdout.txt >> $file_pre
echo -e "#--------------------------------------------------# \n#    CONTAINER 2:                                  # \n#--------------------------------------------------# \n" >> $file_pre
cat $outpath/C2*.stdout.txt >> $file_pre
echo -e "#--------------------------------------------------# \n#    CONTAINER 3:                                  # \n#--------------------------------------------------# \n" >> $file_pre
cat $outpath/C3.stdout.txt >> $file_pre
echo -e "#--------------------------------------------------# \n#    CONTAINER 4:                                  # \n#--------------------------------------------------# \n" >> $file_pre
cat $outpath/C4.stdout.txt >> $file_pre
echo -e "#--------------------------------------------------# \n#    CONTAINER 5:                                  # \n#--------------------------------------------------# \n" >> $file_pre
cat $outpath/C5.stdout.txt >> $file_pre
echo -e "#--------------------------------------------------# \n#    CONTAINER 6:                                  # \n#--------------------------------------------------# \n" >> $file_pre
cat $outpath/C6.stdout.txt >> $file_pre
echo -e "#--------------------------------------------------# \n#    CONTAINER 10:                                  # \n#--------------------------------------------------# \n" >> $file_pre
cat $outpath/C10.stdout.txt >> $file_pre
grep -v "M::process" $file_pre > $file_pre.tmp && grep -v "M::mem_pestat" $file_pre.tmp > $file_pre

aws s3 cp --quiet $file_pre s3://maasslab/$prefix/ \
	&& { aws s3 rm --quiet s3://maasslab/$prefix/ --recursive --exclude "*" \
		--include "C1.stdout.txt" --include "C2*.stdout.txt" --include "C3.stdout.txt" --include "C4.stdout.txt" --include "C5.stdout.txt" --include "C6.stdout.txt" --include "C10.stdout.txt"; }
#--------------------------------------------------------------------------#
