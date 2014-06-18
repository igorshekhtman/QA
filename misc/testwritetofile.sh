#! /bin/sh

export TZ=America/Los_Angeles

timestamp=$(date +'%s')

datestamp=$(date +'%m/%d/%y %r')

find="uploadurl=https://testdr.apixio.com:8443/"

replace="uploadurl=https://dr.apixio.com:8443/"


sed "s/$find/$replace/g" /mnt/indexer0/V30/resources/commsys.ini

# sed -i.bak 's|${line}|${rep}|g' /mnt/indexer0/V30/resources/commsys.ini > /mnt/indexer0/V30/resources/commsys.ini-new

# mv /mnt/indexer0/V30/resources/commsys.ini-new /mnt/indexer0/V30/resources/commsys.ini


# sed -i.bak "s/${line}/${rep}/g" /mnt/indexer0/V30/resources/commsys.ini


# sed -e "s/${line}/${rep}/g" /mnt/indexer0/V30/resources/commsys.ini > /mnt/indexer0/V30/resources/commsys.ini-new

# mv /mnt/indexer0/V30/resources/commsys.ini-new /mnt/indexer0/V30/resources/commsys.ini


# /mnt/indexer0/V30/resources

# new
# uploadurl=https://testdr.apixio.com:8443/

# production url
# uploadurl=https://dr.apixio.com:8443/
