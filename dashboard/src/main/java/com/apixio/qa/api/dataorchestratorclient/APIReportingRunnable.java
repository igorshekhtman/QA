package com.apixio.qa.api.dataorchestratorclient;

import com.apixio.model.patient.Patient;
import com.apixio.model.utility.PatientJSONParser;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;

import java.io.OutputStream;
import java.util.UUID;


public class APIReportingRunnable  implements Runnable{

	DataOrchestratorClient apiClient;
	String patientUUID;
	String documentUUID;
	String[] fields;
	String delimiter;
	OutputStream output;
	String reportMode;
	public APIReportingRunnable (DataOrchestratorClient apiClient, String line, String delimiter, int patientIdIndex, int documentIdIndex, String reportMode, OutputStream output) {
		
		this.apiClient = apiClient;
		this.delimiter = delimiter;
		this.fields = line.split(delimiter, -1);
		if (patientIdIndex >= 0) {
            this.patientUUID = fields[patientIdIndex];
            UUID uuid = UUID.fromString(patientUUID);
        }
        if (documentIdIndex >= 0) {
            this.documentUUID = fields[documentIdIndex];
        }
        this.reportMode = reportMode;
		this.output = output;
	}
	
	public void run() {
		try {
			long start = System.currentTimeMillis();
			//CustomPatientJSONParser pj = new CustomPatientJSONParser();
			PatientJSONParser pj = new PatientJSONParser();
            String patientString = "";
            if (documentUUID != null) {
                patientString = apiClient.getDocumentApo(documentUUID);
            } else {
                patientString = apiClient.getPatientApo(patientUUID);
            }
            Patient patient = pj.parsePatientData(patientString);
			String reportOutput = getReportOutput(patient);
			String outputLine = StringUtils.join(fields, delimiter) + delimiter + reportOutput;
            outputLine += "\n";
			IOUtils.write(outputLine, output);	
			System.out.println(System.currentTimeMillis() + "\tGot report fields \"" + reportOutput + "\" in:\t" + (System.currentTimeMillis() - start));
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}	
	}

    private String getReportOutput(Patient patient) throws Exception {
		String reportOutput = "";
		ReportExtractor extractor = new ReportExtractor(delimiter);
		if (reportMode.equals("scripps")) {
			reportOutput = extractor.getScrippsReport(patient, documentUUID);
		} else if (reportMode.equals("rmc")) {
			reportOutput = extractor.getRmcReport(patient, documentUUID);
		}else if (reportMode.equals("hcpnv")) {
			reportOutput = extractor.getHcpnvReport(patient);
		}else if (reportMode.equals("hpmg")) {
			reportOutput = extractor.getHpmgReport(patient);
		}else if (reportMode.equals("cambia")) {
            reportOutput = extractor.getCambiaReport(patient);
        }
		return reportOutput;
	}


}
