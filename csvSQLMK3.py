import csv
from csv import reader
import copy
import sys
import re
#import pandas as pd
#import numpy as np
from itertools import chain
from suffix_trees import STree

#tables = [   [table1,[col1],[col2],[col3]],
#             [table2,[col1],[col2],[col3]],
#             [table3,[col1],[col2],[col3]]
#         ]

#opens/closes and saves a file:
def readData(fileName):
    if(fileName[-4:]=='.csv'):
        fileName=fileName[-4:]
    try:
        data=open(str(fileName)+".csv")
        rows=[]
        for row in reader(data):
            rows.append(row)
        data.close()
        return rows 
    except:
        return readData(input("File not found... try again: "))

def writeToTxt(statements,queries,fileName):
    with open('createStatements-'+fileName+'.txt','w') as f:
        for line in statements:
            f.write(line[0])
        f.close()
    with open('extractQueries-'+fileName+'.txt','w') as f:
        for line in queries:
            f.write(line)
        f.close()
    print(80*"\n",'~@~Success. \'createStatements-'+fileName+'.txt\' - for building the db, \'extractQueries-'+fileName+'.txt\' - for getting data.~@~')

def clean(item):
    return str(item).strip()

def cleanDataTypes(tables):
    dtDB = ['tinyint','boolean','smallint','mediumint','int','integer','bigint','decimal','float','double','bit','date','time','datetime','timestamp','year','char','varchar','binary','varbinary','tinyblob','blob','mediumblob','longblob','tinytext','text','mediumtext','longtext','enum','set']
    for row in range(0,len(tables)):
        for column in range(1,len(tables[row])):
            if(str(tables[row][column][3]) == ''):
                tables[row][column][3] = '64'
            elif(int(tables[row][column][3]) > 21845):
                tables[row][column][3] = str(255)
            elif(int(tables[row][column][3])<1):
                tables[row][column][3] = str(255)
            flag = 0
            currentDT=(str(tables[row][column][1])).lower()
            for datatype in range(0,len(dtDB)):
                datatypeCheck = str(dtDB[datatype]).lower()
                if(currentDT.find(datatypeCheck)!=-1):
                    if(currentDT == 'nvarchar' or currentDT == ''):
                        tables[row][column][1] = 'varchar'
                    elif(currentDT == 'datetime2'):
                        tables[row][column][1] = 'datetime'
                        tables[row][column][3] = ''
                    flag=1
                    break
                else:
                    tables[row][column][1] = 'varchar'
    return tables

def buildTables(rows):
    db=[]
    dbTablePlaceCount=-1
    previousRange=''
    for row in range(1,len(rows)):
        #below splits are to find table range
        elementsOfRow=copy.deepcopy(rows[row])
        currentTableRange,currentColumnName,currentColumnType,nullType,maxLen = clean(elementsOfRow[2]),clean(elementsOfRow[3]),clean(elementsOfRow[7]),clean(elementsOfRow[6]),clean(elementsOfRow[8])
        if(nullType=='YES'):nullType=' '
        else:nullType=' NOT NULL '
        if(currentTableRange==previousRange):db[dbTablePlaceCount].append([currentColumnName,currentColumnType,nullType,maxLen])
        else:
            previousRange=copy.deepcopy(currentTableRange)
            db.append([currentTableRange])
            dbTablePlaceCount+=1
            db[dbTablePlaceCount].append([currentColumnName,currentColumnType,nullType,maxLen])
    return db

def buildForeignRef(tablesC,relationshipsC):#replaces the 'fkcolname' with it's SQL create statement
    relationships=copy.deepcopy(relationshipsC)
    tables=copy.deepcopy(tablesC)
    for relationship in range(1,len(relationships)):
        for table in range(0,len(tables)):
            tempFKtableNameR,tempFKtableNameC=clean(relationships[relationship][0]),clean(tables[table][0])
            if(tempFKtableNameR==tempFKtableNameC):#if we've found the table we're looking for
                for column in range(1,len(tables[table])):#skip table name, we know where we are
                    colnameR,colnameC,colnameCDT,tableRefR,colRefR,nullType,maxLen=clean(relationships[relationship][1]),clean(tables[table][column][0]),clean(tables[table][column][1]),clean(relationships[relationship][2]),clean(relationships[relationship][3]),tables[table][column][2],clean(tables[table][column][3])
                    if(colnameR==colnameC):
                        tables[table][column]=str(colnameR+' '+colnameCDT+'('+maxLen+')'+' NOT NULL,\n    CONSTRAINT '+'fk_'+colnameR+' FOREIGN KEY ('+colnameR+')\n    REFERENCES '+tableRefR+'('+colRefR+')')
    return tables

def buildPrimaryKey(tablesC, keysC):
    keys,tables=copy.deepcopy(keysC),copy.deepcopy(tablesC)
    for key in range(1,len(keys)):
        for table in range(0,len(tables)):
            tableNameC,tableNameK=clean(tables[table][0]),clean(keys[key][0])
            if(tableNameK==tableNameC):
                for column in range(1,len(tables[table])):
                    fkCheck=tables[table][column]
                    if(type(fkCheck) is not str):
                        colnameC,colnameR,dataType,nullType,maxLen=clean(fkCheck[0]),clean(keys[key][1]),clean(tables[table][column][1]),tables[table][column][2],clean(keys[key][3])
                        if(colnameR==colnameC):
                            if(maxLen=='' or maxLen ==' '):
                                tables[table][column]=str(colnameR+' '+dataType+nullType+',\n'+'    PRIMARY KEY ('+colnameR+')')
                            else:
                                tables[table][column]=str(colnameR+' '+dataType+'('+maxLen+')'+nullType[:-1]+',\n'+'    PRIMARY KEY ('+colnameR+')')
    return tables

def buildRegularCols(tablesC):
    tables=copy.deepcopy(tablesC)
    for table in range(0,len(tables)):
        for column in range(1,len(tables[table])):
            fkCheck=tables[table][column]
            if(type(fkCheck) is not str):#if true means we have what we want, a regular column
                colname,datatype,nullType,maxLen=clean(tables[table][column][0]),clean(tables[table][column][1]),tables[table][column][2],clean(tables[table][column][3])
                if(nullType==' '):nullType=''
                else: nullType=' NOT NULL'
                if(maxLen=='' or maxLen ==' '):tables[table][column]=str(colname+' '+datatype+nullType)
                else:tables[table][column]=str(colname+' '+datatype+'('+maxLen+')'+nullType)
    return tables


def buildStatements(tables):
    oneLineTableP=[]
    oneLineTableC=[]
    for table in range(0,len(tables)):
        forRefFlag = 0
        query,cleanTable='CREATE TABLE ',clean(tables[table][0])
        query=query+cleanTable+' '+'(\n'
        for column in range(1,len(tables[table])):
            line1=str(tables[table][column])
            if(line1.find('FOREIGN')!=-1):
                forRefFlag = 1
            query=query+'    '+line1+',\n'
        query=query[:-2]
        query=query +'\n);\n'
        if(forRefFlag == 1):
            oneLineTableC.append([str(query)])
        else:
            oneLineTableP.append([str(query)])
    oneLineTable = oneLineTableP + oneLineTableC
    return oneLineTable

def dataExtractStatements(tables):
    getData=[]
    for table in range(0,len(tables)):
        tableName=str(tables[table][0])
        getData.append('SELECT * FROM '+tableName+'\n')
    return getData

input(">Make sure you've read the readme.txt file.\n>>Press any key to continue")
fileName=input("Schema file: ")
rawSchema,rawRelationships,rawKeys=readData(fileName),readData(input("Relationships file: ")),readData(input("Primary keys file: "))
extractionTable = copy.deepcopy(rawSchema)
#rawSchema = cleanDataTypes(rawSchema)
writeToTxt(buildStatements(buildRegularCols(buildPrimaryKey(buildForeignRef(cleanDataTypes(buildTables(rawSchema)),rawRelationships),rawKeys))),dataExtractStatements(buildTables(copy.deepcopy(extractionTable))),fileName)

#classy update plan:
#3 builders can be classified
#
#plan for nates colour mapping script
#txt file to store the colours:
#-like: 1 colour per line. first is the base colour. new are appended onto the end.
#
#
#
#

