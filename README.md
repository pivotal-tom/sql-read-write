@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@	
	reqs: python3
	made by Tom for Sam
@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@	

1)open custom query in the client whose db you want to copy, execute and save the output of the following queries:
~~~~~~~~~~~~~~~~schema~~~~~~~~~~~~~~~~
SELECT * FROM INFORMATION_SCHEMA.COLUMNS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~relationships~~~~~~~~~~~~
SELECT
    fk.name 'FK Name',
    tp.name 'Parent table',
    cp.name, cp.column_id,
    tr.name 'Refrenced table',
    cr.name, cr.column_id
FROM 
    sys.foreign_keys fk
INNER JOIN 
    sys.tables tp ON fk.parent_object_id = tp.object_id
INNER JOIN 
    sys.tables tr ON fk.referenced_object_id = tr.object_id
INNER JOIN 
    sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
INNER JOIN 
    sys.columns cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
INNER JOIN 
    sys.columns cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
ORDER BY
    tp.name, cp.column_id
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~primarykeys~~~~~~~~~~~~~~
SELECT 
    so.name 'Table Name',
    c.name 'Column Name',
    t.Name 'Data type',
    c.max_length 'Max Length',
    c.precision ,
    c.scale ,
    c.is_nullable,
    ISNULL(i.is_primary_key, 0) 'Primary Key'
FROM    
    sys.columns c
INNER JOIN 
    sys.types t ON c.user_type_id = t.user_type_id
LEFT OUTER JOIN 
    sys.index_columns ic ON ic.object_id = c.object_id AND ic.column_id = c.column_id
LEFT OUTER JOIN 
    sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
INNER JOIN 
    sysobjects so ON c.object_id = so.id
WHERE
    i.is_primary_key = 1 and 
    so.xtype = 'U'
Order By 'Table Name', 'Column Name'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
2)put the .csv files in the same directory as csvSQL.py
3)open this directory in the terminal
4)enter 'python3 csvSQL.py' in the terminal, without ' '
5)once the program has finished executing you will have two files:
	-createStatements.txt statements for building the db
	-extractQueries.txt queries for getting data from linnworks to populate the db

~~~~~~~~~~~~~~END~~~~~~~~~~~~~~~~~~~~~






