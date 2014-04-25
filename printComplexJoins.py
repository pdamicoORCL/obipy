#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  printJoins_02.py
#  
#  Copyright 2013 Phil D'Amico
#  
#  

import datetime
import sys
import os
import xml.etree.ElementTree as ET


def getFullLineage(theRef, baseDir):

  rpd       = '{http://www.oracle.com/obis/repository}'

  lineage={}
  lineage['Database']=''
  lineage['PhysicalCatalog']=''
  lineage['Schema']=''
  lineage['PhysicalTable']=''
  lineage['AnalyticWorkspace']=''
  lineage['AWDimension']=''
  lineage['AWCube']=''
  
  tableRef              = theRef.replace('"','').strip()
  refPath               = theRef.split('#')[0]
  refFile               = baseDir + refPath
  refXml                = ET.parse(refFile)

  objectType            = refXml.getroot().tag.replace(rpd,'')

  lineage[objectType]   = refXml.getroot().attrib['name']

  while 'containerRef' in refXml.getroot().attrib:

    parentRef           = refXml.getroot().attrib['containerRef']

    parentPath          = parentRef.split('#')[0]

    parentFile          = baseDir + parentPath

    refXml              = ET.parse(parentFile)

    objectType          = refXml.getroot().tag.replace(rpd,'')

    lineage[objectType] = refXml.getroot().attrib['name']

  return lineage


def print_banner():

  '''
  This simple routine prints a banner with the name of the script, the version
  and the author, surrounded by dotted lines. You can safely comment out the 
  call to this routine if you want; it doesn't update any variables or otherwise
  do anything that the rest of the script is expecting
  '''
  # Banner
  #
  banner_width = 80
  print '-'*banner_width
  print sys.argv[0].center(banner_width)
  print "Oracle BI rpd Documentation version  %s".center(banner_width)  % __version__
  print "Author: Phil D'Amico (phil.damico@oracle.com)".center(banner_width)
  print rootDir.center(banner_width)
  ctime = datetime.datetime.strftime(datetime.datetime.now(), "%b %d, %Y %I:%M %p")
  print ctime.center(banner_width)
  print '-'*banner_width + '\n'

def print_The_Complex_Joins():
  
  lstPhyTables = []
  
  filesRead = 0
  filesTotal = len(os.listdir('.'))
  
  for pTable in os.listdir('.'):
    
    # 11/19/2013 09:52
    # Debug
    filesRead += 1
    print '%-5s\t%-5s\t%s' % (filesRead, filesTotal, pTable.replace('\n',''))
    # End of Debug
    
    pXml          = ET.parse(pTable.replace('\n',''))

    theJoin       = ''

    table1Ref     = pXml.getroot().attrib['table1Ref']

    table2Ref     = pXml.getroot().attrib['table2Ref']

    if pXml.find('.//{0}ExprTextDesc'.format(rpd)).text is not None:
      theJoin     = pXml.find('.//{0}ExprTextDesc'.format(rpd)).text.replace('\n', ' ')
    else:
      print 'None'

    
    dictLineage = getFullLineage(table1Ref, rootDir)
    print dictLineage

    db1  = dictLineage['Database']
    pc1  = dictLineage['PhysicalCatalog']
    sc1  = dictLineage['Schema']
    ph1  = dictLineage['PhysicalTable']
    aw1  = dictLineage['AnalyticWorkspace']
    awd1 = dictLineage['AWDimension']
    awc1 = dictLineage['AWCube']

    dictLineage = getFullLineage(table2Ref, rootDir)
    #print dictLineage

    db2  = dictLineage['Database']
    pc2  = dictLineage['PhysicalCatalog']
    sc2  = dictLineage['Schema']
    ph2  = dictLineage['PhysicalTable']
    aw2  = dictLineage['AnalyticWorkspace']
    awd2 = dictLineage['AWDimension']
    awc2 = dictLineage['AWCube']

    if awc1 != '':
      join_out.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % ( \
                      aw1, \
                      pc1, \
                      awd1, \
                      awc1, \
                      aw2, \
                      pc2, \
                      awd2, \
                      awc2, \
                      theJoin)
                    )
    else:
      join_out.write  (
                        '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % \
                        ( \
                          db1, \
                          pc1, \
                          sc1, \
                          ph1, \
                          db2, \
                          pc2, \
                          sc2, \
                          ph2, \
                          theJoin
                        )
                      )


def main():
  

  '''
  First we loop through all the files in the "PhysicalTable" directory
  We store the "key" (Database + schema + table) and the xml File name
  in a 2-dimensional list (i.e. a "list of lists")
  We do this so we can sort the list so the "main" loop (the one that
  gets all the joined tables) will output in sorted order
  '''  

  print_The_Complex_Joins()


  return 0

if __name__ == '__main__':

  __version__ = "0.5"
  
  rpd       = '{http://www.oracle.com/obis/repository}'

  if len(sys.argv)>1 : 

    rootDir = sys.argv[1]

    if rootDir.strip()[-1] == '/' : rootDir = rootDir.strip()[:-1]

  else:

    rootDir   = os.getcwd()

  print_banner()
  
  if not os.path.isdir(rootDir + '/oracle/bi/server/base/ComplexJoin'):

    print 'No Directory: %s' % (rootDir + '/oracle/bi/server/base/ComplexJoin')

    sys.exit()
  


  joinCsvFileName = rootDir.split('/')[-1] + '.complex.joins.csv'

  join_out = open(joinCsvFileName, 'w')

  join_out.write("db1\tpc1\tsc1\tph1\tdb2\tpc2\tsc2\tph2\ttheJoin\n")
  
  currentDir = os.getcwd()
  os.chdir(rootDir + '/oracle/bi/server/base/ComplexJoin')

  main()

  join_out.close()

  print ''
  print '\n\nOutput file: %s\n\n' % joinCsvFileName
