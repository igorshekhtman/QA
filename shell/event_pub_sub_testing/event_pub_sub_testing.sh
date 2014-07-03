#! /bin/sh
export TZ=America/Los_Angeles
timestamp=$(date +'%s')
datestamp=$(date +'%m/%d/%y %r')

#! ======================= Initializing variables ===============================
change=
usrname=
pw=
key=
test=
i=
environment="s"  
stagindrurl="uploadurl=https://testdr.apixio.com:8443/"  
productiondrurl="uploadurl=https://dr.apixio.com/"  
configfile="commsys.ini"
#! ==============================================================================
clear

echo "==========================================================================="
echo "To avoid a collision, please select Indexer and it's related work folders."
echo "Please select Indexer folder # you are planning to use for this test:"
echo "==========================================================================="
echo "0. Indexer0"
echo "1. Indexer1"
echo "2. Indexer2"
echo "3. Indexer3"
echo "4. Indexer4"
echo "5. Indexer5"
echo "==========================================================================="
read -p "Confirm and select available Indexer number to run: " i

if [ "$i" -ge 0 ] && [ "$i" -le 5 ]; then
	echo "==========================================================================="
	echo "Indexer$i has been selected for this test ..."
	echo "==========================================================================="
else
	echo "==========================================================================="
	echo "Error: Indexer$i does not exist, exiting script ..."
	echo "==========================================================================="
	exit
fi

echo "==========================================================================="
echo "Please select test environment (default value is STAGING):"
echo "==========================================================================="
echo "S. Staging"
echo "P. Production"
echo "==========================================================================="
#read -p "Select test environment to run your test (S/P)? " -n 1
#echo
#if [[ $REPLY =~ ^[Pp]$ ]]; then
#	sed -i s/testdr/dr/g /mnt/indexer$i/V30/resources/$configfile
#	echo "==========================================================================="
#	echo "Environment has been set for PRODUCTION ..."
#	echo "==========================================================================="
#	environment="p"
#else
#	sed -i s/dr/testdr/g /mnt/indexer$i/V30/resources/$configfile
#	echo "==========================================================================="
#	echo "Environment has been set for STAGING ..."
#	echo "==========================================================================="
#	environment="s"
#fi


#! ====== DELETE ANY PRE-EXISTING DOCUMENTS FROM WORK AND SOURCE FOLDERS ========
echo "==========================================================================="
echo "Removing old and re-creating new work folders, please wait ..."
echo "==========================================================================="
rm -rf /mnt/indexer$i/WORK
mkdir /mnt/indexer$i/WORK
rm -rf /mnt/indexer$i/TRANSMIT
mkdir /mnt/indexer$i/TRANSMIT
rm -rf /mnt/indexer$i/SOURCE
mkdir /mnt/indexer$i/SOURCE
echo "==========================================================================="
echo "Clean up from previous test execution is now completed ..."
echo "==========================================================================="

echo "==========================================================================="
echo "1. SANITY TEST - 2 PATIENTS 8 DOCUMENTS NO OCR"
echo "2. SANITY TEST - 2 PATIENTS 16 DOCUMENTS WITH OCR"
echo "3. COORDINATOR STRESS TEST - 1000 TXT 1000 PDF WITH OCR (ORG 1)"
echo "4. COORDINATOR STRESS TEST - 1000 TXT 1000 PDF WITH OCR (ORG 2)"
echo "5. TEST - 100 CCRs"
echo "6. TEST - 100 CCDs"
echo "7. OCR STRESS TEST - 10, 20, 30, 49, 50, 51, 100, 200, 300MB PDF DOCUMENTS"
echo "8. OCR STRESS TEST - 300, 400, 500, 600, 700, 800MB PDF DOCUMENTS"
echo "9. STRESS TEST - 1 PATIENT 2000 EACH TXT RTF DOC DOCMENTS 6000 TOTAL"
echo "10. STRESS TEST - 20,000 PATIENTS 1 TXT DOCUMENT EACH"
echo "11. STRESS TEST - 50 PATIENTS 200 TXT 200 PDF DOCUMENTS EACH 20,000 TOTAL"
echo "12. HCC DEMO 2 PATIENTS 3 DOCUMENTS"
echo "13. HCC TRAINING 1 PATIENT 32 DOCUMENTS "
echo "14. STRESS TEST - 500 PATIENTS 30 PDF TXT RTF JPG DOC DOCUMENTS 15,000 TOTAL"
echo "15. STRESS TEST - 500 PATIENTS 30 PDF TXT RTF JPG DOC DOCUMENTS 15,000 TOTAL"
echo "16. NEGATIVE TEST - BAD CCR, CCD, PDF, JPG, RTF, TXT, DOC DOCUMENTS 3 OF EACH"
echo "17. STRESS TEST (LARGE) - 10,000 PATIENTS 1 TXT DOCUMENT EACH"
echo "18. STRESS TEST (MEDIUM) - 5,000 PATIENTS 1 TXT DOCUMENT EACH"
echo "19. STRESS TEST (SMALL) - 1,000 PATIENTS 1 TXT DOCUMENT EACH"
echo "20. CARE OPTIMIZER TEST - ONE LARGE PATIENT WITH 5000 TXT DOCUMENTS"
echo "==========================================================================="
read -p "Select test number to run: " test

case $test in
	1) cp -avr /mnt/testdata/SanityTwoPatientsAllFileTypesNoOCR/Catalogs/20131025_105656 /mnt/indexer$i/SOURCE/ ;;
	2) cp -avr /mnt/testdata/SanityTwoPatientsAllFileTypes/Catalogs/20131024_024747 /mnt/indexer$i/SOURCE/ ;;
	3) cp -avr /mnt/testdata/CoordinatorTest1000TXT1000PDFOrg1/catalog/201312030511258541 /mnt/indexer$i/SOURCE/ ;;
	4) cp -avr /mnt/testdata/CoordinatorTest1000TXT1000PDFOrg2/catalog/201312030519356111 /mnt/indexer$i/SOURCE/ ;;
	5) cp -avr /mnt/testdata/100CCRs/catalog/20131127_025742 /mnt/indexer$i/SOURCE/ ;;
	6) cp -avr /mnt/testdata/100CCDs/catalog/20131127_033223 /mnt/indexer$i/SOURCE/ ;;
	7) cp -avr /mnt/testdata/10_20_30_49_50_51_100_200_300Mb_PDFs/catalog/123456789012345678 /mnt/indexer$i/SOURCE/ ;;
	8) cp -avr /mnt/testdata/300_400_500_600_700_800Mb_PDFs/catalog/123456789012345679 /mnt/indexer$i/SOURCE/ ;;
	9) cp -avr /mnt/testdata/1Patient2000EachTxtDocRtfDocuments/catalog/201312040831097892 /mnt/indexer$i/SOURCE/ ;;
	10) cp -avr /mnt/testdata/20000Patients1TxtDocumentEach/catalog/201312040241295911 /mnt/indexer$i/SOURCE/ 
	    cp -avr /mnt/testdata/20000Patients1TxtDocumentEach/catalog/201312051119133009 /mnt/indexer$i/SOURCE/
	    cp -avr /mnt/testdata/20000Patients1TxtDocumentEach/catalog/201312050842107850 /mnt/indexer$i/SOURCE/	;;
	11) cp -avr /mnt/testdata/50Patients200Txt200PdfEach/catalog/201312060250197522 /mnt/indexer$i/SOURCE/ ;;
	12) cp -avr /mnt/testdata/HCC_Demo/catalog /mnt/indexer$i/SOURCE/ ;;
	13) cp -avr /mnt/testdata/HCC_Training/catalog /mnt/indexer$i/SOURCE/ ;;
	14) cp -avr /mnt/testdata/500Patients15000DocumentsTotal/catalog/201312170839136460 /mnt/indexer$i/SOURCE/ ;;
	15) cp -avr /mnt/testdata/500Patients15000DocumentsTotal-2/catalog/201312180923217633 /mnt/indexer$i/SOURCE/ 
           cp -avr /mnt/testdata/500Patients15000DocumentsTotal-2/catalog/201312191043091606 /mnt/indexer$i/SOURCE/		
           cp -avr /mnt/testdata/500Patients15000DocumentsTotal-2/catalog/201312191051107481 /mnt/indexer$i/SOURCE/ ;;
	16) cp -avr /mnt/testdata/NegativeTestData-1/catalog /mnt/indexer$i/SOURCE/ ;;
	17) cp -avr /mnt/testdata/10000Patients1TxtDocumentEach/catalog /mnt/indexer$i/SOURCE/ ;;
	18) cp -avr /mnt/testdata/5000Patients1TxtDocumentEach/catalog /mnt/indexer$i/SOURCE/ ;;
	19) cp -avr /mnt/testdata/1000Patients1TxtDocumentEach/catalog /mnt/indexer$i/SOURCE/ ;;
	20) cp -avr /mnt/testdata/Largepatient_5000_Txt_Documents/catalog/201404070121338174 /mnt/indexer$i/SOURCE/ ;;
	*) 	echo "==========================================================================="
		echo "Error: Invalid test number selection, exiting script" 
		echo "==========================================================================="
	   	exit ;;
esac

echo "============================================================================"
echo "Catalog files from TestData set were copied to Indexer's [SOURCE] folder ..."
echo "============================================================================" 

read -p "Change Apixio Patient Optimizer username and password (y/n)? " -n 1
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
echo "==========================================================================="
echo "  "
echo "Please update username, password and key for Indexer$i CommSys.ini file"
if [ "$environment" == "s" ]; then
	echo "  "
	echo "Use the following key value for STAGING environment:"
	echo "  "
	echo "V01_8p1x1o1825sanmateocalifornia9440"
else
	echo "  "
	echo "Use the following key value for PRODUCTION environment:"
	echo "  "
	echo "V01_dWbZtN56Hnwez6jR5Tfjx25bdfj8GVJt"
fi
echo "  "
echo "==========================================================================="
cd /mnt/indexer$i/V30
java -cp apixio-indexer-3.1.0.jar com.apixio.indexer.util.Setup
echo "==========================================================================="
echo "Username, password and key values are now updated ..."
echo "==========================================================================="
fi

#! ====================== RUN specified Indexer ==================================
echo "============================================================================"
echo "Starting Indexer$i <Cltr-C> to exit ..."
echo "============================================================================" 
cd /mnt/indexer$i/V30
java -jar apixio-indexer-3.1.0.jar
echo "  "
echo "Indexer$i is now stopped ..."
echo "  "
