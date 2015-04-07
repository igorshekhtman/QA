# Use the right thing: 
USE Router_stg;

# This is the name of a project to target for a reset:
SET @proj = 'foo';

# Turn off foreign key checks on a temporary basis: 
SET FOREIGN_KEY_CHECKS=0;

# Turn off safe update mode:
SET SQL_SAFE_UPDATES = 0;

# Clean tables: 
DELETE FROM Finding_Annotation fa WHERE fa.annotations_id IN (
  SELECT a.id FROM Annotation a WHERE a.project = @proj);
DELETE FROM Annotation WHERE project = @proj;
DELETE FROM ServedOpportunity WHERE id IN (
  SELECT so.id FROM ServedOpportunity so INNER JOIN Opportunity o ON o.id = so.opId WHERE o.project = @proj);

# Cleaning up assigned code is tricky, because it is filled both programatically and by front end: 
CREATE TABLE AssignedCode_BK LIKE AssignedCode;
INSERT AssignedCode_BK SELECT * FROM AssignedCode;
DELETE FROM AssignedCode WHERE id NOT IN (
  SELECT ac.id FROM Finding f INNER JOIN AssignedCode_BK ac ON ac.id = f.code_id);
DROP TABLE AssignedCode_BK;

# Modify the status column in the opportunity table: 
UPDATE Opportunity o SET o.user='',o.status='Routable' WHERE o.project = @proj;

# Turn FK checks back on: 
SET FOREIGN_KEY_CHECKS=1;

# Turn off safe update mode:
SET SQL_SAFE_UPDATES = 1;