package com.apixio.qa.api.dataorchestratorclient;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.Scanner;
import java.util.concurrent.*;

public class MultiThreadAPIReportingClient {
	public static void execute(String fileName, String reportMode, String delimiter, int patientIndex, int documentIndex, DataOrchestratorClient client, int numThreads) throws Exception {

		BlockingQueue<Runnable> blockingQueue = new ArrayBlockingQueue<Runnable>(numThreads);
	    RejectedExecutionHandler rejectedExecutionHandler = new ThreadPoolExecutor.CallerRunsPolicy();
	    ExecutorService executor =  new ThreadPoolExecutor(numThreads, numThreads, 0L, TimeUnit.MILLISECONDS, blockingQueue, rejectedExecutionHandler);
		
		Scanner scanner = new Scanner(new FileInputStream(fileName));
        String outputFileName = fileName + "_" +  System.currentTimeMillis() +  ".out";
		OutputStream output = new FileOutputStream(outputFileName);

		while (scanner.hasNextLine()) {
			String line = scanner.nextLine();
            try {
    			Runnable worker = new APIReportingRunnable(client,line, delimiter, patientIndex, documentIndex, reportMode, output);
    			executor.execute(worker);
            } catch (Exception ex) {
            	System.out.println("The plane is broken: " + ex.toString());
            }
		}
        executor.shutdown();
        while (!executor.isTerminated()) {
        }
		scanner.close();
	}
}
