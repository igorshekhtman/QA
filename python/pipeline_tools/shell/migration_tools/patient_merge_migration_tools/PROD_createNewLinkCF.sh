# for patient merge migration we also migrate link table to apx_cfLink_new

java -cp apixio-datasource-1.7.1.jar com.apixio.dao.cmdline.CreateColumnFamilies --hosts 10.174.97.35 --columnFamily apx_cfLink_new --orgId 1 --output createdCF.log
