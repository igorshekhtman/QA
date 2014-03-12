@ECHO OFF
REM ===================== Initializing variables ==============================
SET change=
SET usrname=
SET pw=
SET key=
SET test=
SET i=
REM ===========================================================================
REM SET /P usrname=Please enter apixio patient optimizer user name:
REM SET /P pw=Please enter apixio patient optimizer password:
REM SET key=V01_8p1x1o1825sanmateocalifornia9440
REM ===========================================================================
CLS
ECHO ===========================================================================
ECHO NOTE: ONLY ONE USER CAN RUN ONE INDEXER FROM ANY ONE FOLDER TO AVOID ANY 
ECHO COLLISION
ECHO SELECT INDEXER FOLDER YOU ARE PLANNING TO USE:
ECHO ===========================================================================
ECHO 0. Indexer0
ECHO 1. Indexer1
ECHO 2. Indexer2
ECHO 3. Indexer3
ECHO 4. Indexer4
ECHO 5. Indexer5
ECHO ===========================================================================
SET /P i=Confirm and select available Indexer number to run:
CD Z:\Indexer%i%\V30

REM ===== DELETE ANY PRE-EXISTING DOCUMENTS FROM WORK AND SOURCE FOLDERS =======
ECHO ===========================================================================
ECHO Removing old and re-creating new work folders, please wait ...
ECHO ===========================================================================
RMDIR Z:\Indexer%i%\SOURCE /s/q
MKDIR Z:\Indexer%i%\SOURCE
RMDIR Z:\Indexer%i%\TRANSMIT /s/q
MKDIR Z:\Indexer%i%\TRANSMIT
RMDIR Z:\Indexer%i%\WORK /s/q
MKDIR Z:\Indexer%i%\WORK
ECHO ===========================================================================
ECHO Clean up finished ...
ECHO ===========================================================================

ECHO ===========================================================================
ECHO 1. SANITY TEST - 2 PATIENTS 8 DOCUMENTS NO OCR
ECHO 2. SANITY TEST - 2 PATIENTS 16 DOCUMENTS WITH OCR
ECHO 3. TEST - 2 PATIENTS 980 DOCUMENTS EACH WITH OCR
ECHO 4. TEST - 500 PATIENTS 500 TXT DOCUMENTS TOTAL
ECHO 5. STRESS TEST - 2000 PATIENTS 2000 TXT DOCUMENTS TOTAL
ECHO 6. STRESS TEST - 1000 PATIENTS 2 TXT AND PDF EACH 20K TOTAL
ECHO 7. COORDINATOR STRESS TEST - 1000 TXT 1000 PDF WITH OCR (ORG 1)
ECHO 8. COORDINATOR STRESS TEST - 1000 TXT 1000 PDF WITH OCR (ORG 2)
ECHO 9. OCR TEST - 2 PATIENTS 2000 PDF ONE-PAGE DOCUMENTS EACH
ECHO 10. OCR SANITY TEST - 1 PATIENT 1 3-PAGE PDF DOCUMENT
ECHO 11. TEST - 1000 PATIENTS 2 DOC EACH 5MB EACH DOC (PDF AND TXT)
ECHO 12. TEST - 10,000 PATIENTS 2 DOC EACH 1MB EACH DOC (PDF AND TXT) OCR
ECHO 13. TEST - 10,000 PATIENTS 2 DOC EACH 1MB EACH DOC (PDF AND TXT) NO IMAGES
ECHO 14.
ECHO 15.
ECHO 16.
ECHO 17.
ECHO 18.
ECHO 19. 
ECHO 20. MONSTER STRESS TEST - TEN THOUSAND DOCUMENT (NOT READY)
ECHO ===========================================================================
SET /P test=Select test number to run:
IF %test% == 1 GOTO Test1
IF %test% == 2 GOTO Test2
IF %test% == 3 GOTO Test3
IF %test% == 4 GOTO Test4
IF %test% == 5 GOTO Test5
IF %test% == 6 GOTO Test6
IF %test% == 7 GOTO Test7
IF %test% == 8 GOTO Test8
IF %test% == 9 GOTO Test9
IF %test% == 10 GOTO Test10
IF %test% == 11 GOTO Test11
IF %test% == 12 GOTO Test12
IF %test% == 13 GOTO Test13

:Test1
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\SanityTwoPatientsAllFileTypesNoOCR\Catalogs\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test2
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\SanityTwoPatientsAllFileTypes\Catalogs\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test3
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\TwoPatients980DocumentsEach\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test4
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\500Patients500TxtDocuments\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test5
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\2000Patients2000TxtDocuments\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test6
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\10000Patients2DocumentsEach\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test7
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\CoordinatorTest1000TXT1000PDFOrg1\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test8
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\CoordinatorTest1000TXT1000PDFOrg2\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test9
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\OCR2Patients2000DocumentsOnePageEach\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test10
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\OCRSanityTest\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test11
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\1000Patients2DocEach5MbEachDoc\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test12
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\10kPatients100DocumentsEach\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername
:Test13
ECHO ===========================================================================
ECHO Copying catalog files to source folder, please wait ...
ECHO ===========================================================================
xcopy Z:\TestData\10kPatients100DocumentsEachNoImages\catalog\*.* Z:\Indexer%i%\SOURCE\*.* /s/e/c/y
GOTO Changeusername


:Changeusername
SET /P change=Change apixio patient optimizer username and password (Y/N):
IF %change% == N GOTO Runindexer
IF %change% == n GOTO Runindexer
IF %change% == No GOTO Runindexer
IF %change% == no GOTO Runindexer
ECHO ===========================================================================
ECHO use the following key value for staging:
ECHO V01_8p1x1o1825sanmateocalifornia9440
ECHO ===========================================================================
java -cp apixio-indexer-3.1.0.jar com.apixio.indexer.util.Setup
:Runindexer
java -jar apixio-indexer-3.1.0.jar
CD Z:\Automation
ECHO Indexer%i% stopped ...