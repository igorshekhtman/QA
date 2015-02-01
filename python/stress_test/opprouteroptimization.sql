# Use the right thing: 
USE Router_stg; 

# Turn off foreign key checks on a temporary basis: 
SET FOREIGN_KEY_CHECKS=0; 

# Turn off safe update mode:
SET SQL_SAFE_UPDATES = 0;

# Clean tables: 
DELETE FROM Finding_Annotation; 
DELETE FROM Annotation; 
DELETE FROM ServedOpportunity; 
DELETE FROM RuleDescriptor; 
DELETE FROM Provider; 
DELETE FROM UserMetric; 
DELETE FROM MetricSection_UserMetric; 

# Cleaning up assigned code is tricky, because it is filled both programmatically and by front end. 
CREATE TABLE AssignedCode_BK LIKE AssignedCode; 
INSERT AssignedCode_BK SELECT * FROM AssignedCode; 
DELETE FROM AssignedCode 
WHERE id NOT IN ((SELECT ac.id 
                  FROM Finding f INNER JOIN AssignedCode_BK ac ON ac.id = f.code_id)); 
DROP TABLE AssignedCode_BK; 

# Modify the status column in the opportunity table: 
UPDATE Opportunity o SET o.user='',o.status='Routable'; 

# Turn FK checks back on: 
SET FOREIGN_KEY_CHECKS=1;