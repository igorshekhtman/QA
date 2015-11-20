import apxapi
d = apxapi.APXSession("alarocca@apixio.com",environment=apxapi.DEV)
project = d.useraccounts.get_project('PRHCC_cd8050db-298e-4933-b2b5-75e887c77770').json()
patient_uuids = [uuid.strip() for uuid in 
    d.dataorchestrator.get_archive_document(project['pdsExternalID'],
                                            project['patientList']).text.split('\n')]
titles = set()
for patient_uuid in patient_uuids:
    try:
        events = d.dataorchestrator.patient_events(patient_uuid).json()['eventTypes']
        for event in events:
            titles.add(event['evidence']['attributes']['title'])
    except:
        print('no events for ' + patient_uuid)
with open('doc_title_filters.txt','w') as doc_title_filters:
    for title in titles:
        doc_title_filters.write(title + '\n')