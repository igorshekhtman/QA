count=0
filenumber=0
mkdir cf$1_patKeys_grouped
for file in cf$1_patKeys/*
        do
            if [ "$count" = "0" ]
            then
                filenumber=$((filenumber+1))
		mkdir cf$1_patKeys_grouped/sub-$filenumber
            fi

            count=$((count+1))
            cp $file cf$1_patKeys_grouped/sub-$filenumber

            if [ "$count" = "$2" ]
            then
                count=0
            fi
        done
