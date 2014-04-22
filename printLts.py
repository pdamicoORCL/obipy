#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  getLts_levels_03.py
#  
#  Copyright 2013 Phil D'Amico (phil.damico@oracle.com)
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  

import os
import sys
import xml.etree.ElementTree as ET
import subprocess
import datetime
import sqlite3

def print_all_columns(logicalTableXml):
  pass
  #print ET.parse(lstLogicalTable[3]).getroot().attrib['name']
  columnsInLogicalTable = logicalTableXml.findall('.//{0}ColumnMapping/{0}LogicalColumnExpr/{0}ObjectRefList/{0}RefObject'.format(RPD))
  for logicalColumn in columnsInLogicalTable:
    logicalColumnRef = logicalColumn.attrib['objectRef']
    lPath = logicalColumnRef.split('#')[0].split('/')[-2] + '/' 
    lFileName  = logicalColumnRef.split('#')[0].split('/')[-1]
    lMdsId     = logicalColumnRef.split('#')[1]
    #print lMdsId
    ltXmlFile = ET.parse('../' + lPath + lFileName)
    #print ltXmlFile.getroot().attrib['name']
    print '\t\t\t%s' % ltXmlFile.find( ('.//{0}LogicalColumn[@mdsid="' + lMdsId + '"]').format(RPD) ).attrib['name']
    

def print_report():
  #conn=sqlite3.connect('temp.db')
  print '\n'
  banner_width = 80
  print '-'*banner_width
  print sys.argv[0].center(banner_width)
  print "Oracle BI RPD Doc Utilities Version  %s".center(banner_width)  % __version__
  print "Print Logical Tabile Sources and Levels".center(banner_width)
  print "Logical Tables, ranked by # of Logical Table Sources".center(banner_width)
  ctime = datetime.datetime.strftime(datetime.datetime.now(), "%b %d, %Y %I:%M %p")
  print ctime.center(banner_width)
  #print allNames
  print '-'*banner_width + '\n'

  with conn:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor() 
    cur.execute("select bm, lt, count(distinct lts) theCount from vw_lts group by bm, lt order by 3 desc")
    rows = cur.fetchall()
    print '%-40s\t%-40s\t%s' % ("Business Model", "Logical Table", "Count")
    print '%-40s\t%-40s\t%s\n' % ('-'*len("Business Model"), '-'*len("Logical Table"), '-'*len("Count"))
    for row in rows:
      print '%-40s\t%-40s\t%5d' % (row['bm'], row['lt'], row['theCount'] )


def getBusinessModel(businessModelRef):

  businessModelPath     = businessModelRef.split('#')[0].split('/')[-2] + '/' 
  businessModelFileName = businessModelRef.split('#')[0].split('/')[-1]
  businessModel         = '../' + businessModelPath + businessModelFileName

  return ET.parse(businessModel).getroot().attrib['name']

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
  print "Oracle BI rpd version  %s".center(banner_width)  % __version__
  print "Author: Phil D'Amico (phil.damico@oracle.com)".center(banner_width)
  ctime = datetime.datetime.strftime(datetime.datetime.now(), "%b %d, %Y %I:%M %p")
  print ctime.center(banner_width)
  #print allNames
  print '-'*banner_width + '\n'

def main():

  global RPD
  RPD                 = '{http://www.oracle.com/obis/repository}'
  
  #TEXT_FRAGMENTATION  = '(Fragmentation)'
  TEXT_FRAGMENTATION  = '***** Fragmentation (next line has fragment definition) *****'
  TEXT_CONTENT_FILTER = '***** Content Filter *****'

  rootDir   = '/oracle/bi/server/base'

  #baseDir   = '/home/pdamico/temp/mdsXml/sia_only'
  #baseDir   = '/home/pdamico/temp/mdsXml/amazon'
  
  if len(sys.argv)>1 : 
    baseDir = sys.argv[1]
  else:
    baseDir   = '/home/pdamico/Desktop/sampleapp'
  #baseDir   = "/media/pdamico/PASS500GB/backup/mint64/Desktop/sampleapp"

  lts_out   = open('getLts_levels.csv', 'w')
  template  = '%s|%s|%s|%s|%s\n'
  
  # .csv File Header
  lts_out.write(template % ("LogTable", "LogTableSource", "BusModel", "Dimension", "Level"))

  os.chdir(baseDir + rootDir + '/LogicalTableSource')

  allLtsFiles = []
  print "Have to look through %s files" % len(os.listdir('.'))

  for ltsFile in os.listdir('.'):

    logicalTableRef     = ET.parse(ltsFile)\
                                          .getroot() \
                                          .attrib['logicalTableRef']
                                          
    logicalTableXmlFileName = baseDir + logicalTableRef.split("#")[0]
    
    logicalTableXmlFile     = ET.parse(logicalTableXmlFileName)

    logicalTableName        = logicalTableXmlFile.getroot().attrib['name']

    businessModelName       = getBusinessModel(logicalTableXmlFile\
                                          .getroot()
                                          .attrib['subjectAreaRef'] )

    sortKey = businessModelName +  \
              logicalTableName  +  \
              ET.parse(ltsFile).getroot().attrib['name']
    
    allLtsFiles.append([sortKey, businessModelName, logicalTableName, ltsFile])

  #print allLtsFiles

  currentLogicalTable = ""

  for lTable in sorted(allLtsFiles):

    ltsXmlFile  = ET.parse(lTable[3])

    ltsName     = ltsXmlFile.getroot().attrib['name']

    lTableFile  = ltsXmlFile.getroot().attrib['logicalTableRef'].split('#')[0]

    lTableName  = ET.parse(baseDir + lTableFile).getroot().attrib['name']

    # Check for fragmentation
    canCombine      = ""
    fragmentContent = ""
    if 'canCombine' in ltsXmlFile.getroot().attrib:
      if ltsXmlFile.getroot().attrib['canCombine'] == "true" : 
        canCombine = TEXT_FRAGMENTATION
        if ltsXmlFile.find('.//{0}FragmentContent/{0}ExprTextDesc'.format(RPD)) is not None:
          fragmentContent = ltsXmlFile.find('.//{0}FragmentContent/{0}ExprTextDesc'.format(RPD)).text
          if fragmentContent is not None: fragmentContent = fragmentContent.replace('\n','')

    
    # Proactively get the number of levels defined. That way, if it's only one level, we can print it
    # on the same line, which saves space.
    allLevels =''
    if      ltsXmlFile.find('.//{0}GroupBy/{0}ExprTextDesc'.format(RPD)) is not None \
        and ltsXmlFile.find('.//{0}GroupBy/{0}ExprTextDesc'.format(RPD)).text is not None:

      allLevels = ltsXmlFile.find('.//{0}GroupBy/{0}ExprTextDesc'.format(RPD)).text.replace(' GROUPBYLEVEL(','')[:-1]
      allLevels = allLevels.replace('",', '"|').split('| ')
      allLevels.sort()

    # Print the Content Filter, if there is one
    contentFilter = ""
    if ltsXmlFile.find('.//{0}WhereClause/{0}ExprTextDesc'.format(RPD)) is not None:
      if ltsXmlFile.find('.//{0}WhereClause/{0}ExprTextDesc'.format(RPD)).text is not None:
        if len(ltsXmlFile.find('.//{0}WhereClause/{0}ExprTextDesc'.format(RPD)).text.strip())>0:
          #print a.getroot().attrib['name']
          contentFilter = ltsXmlFile.find('.//{0}WhereClause/{0}ExprTextDesc'.format(RPD)).text.replace('\n','')
          print '\n\t\t%s\n\t\t%s\n' % (TEXT_CONTENT_FILTER, contentFilter)

    if currentLogicalTable <> lTableName:
      print '\n"%s"."%s"' % (lTable[1], lTableName)
      currentLogicalTable = lTableName
    
    print '\n\t"%s"' % (ltsName)
      

    if canCombine == TEXT_FRAGMENTATION:
      print "\n\t\t%s\n\t\t%s\n" %  (canCombine, fragmentContent)




    #Print the levels of the LTS
    if len(allLevels) > 0:
      for y in allLevels:
        #print '\t' + y
        levels = y.split('"."')
        bm     = levels[0].replace('"','')
        dim    = levels[1].replace('"','')
        lvl    = levels[2].replace('"','')

        lts_out.write(template % (lTableName.encode('utf-8'), ltsName.replace('"','').encode('utf-8'), bm.encode('utf-8'), dim.encode('utf-8'), lvl.encode('utf-8')))
        #print '\t' + y.replace('"' + bm + '".', "")
        print '\t\t%-40s %s' % (dim.encode('utf-8'), lvl.encode('utf-8'))

        ins_line =  '%s||||%s||||%s||||%s||||%s||||%s||||%s||||%s||||%s' % \
                    (lTable[3], bm, lTableName, ltsName, dim, lvl, contentFilter, canCombine, fragmentContent)
        ins_list =  ins_line.split('||||')
        #print len(ins_list)
        
        param = ['?' for item in ins_list ]
        sql = 'INSERT INTO ltslevels (sXmlFileName, sBusinessModel, sLogicalTable, sLogicalTableSource, sDimension, sLevel, sContentFilter, sFragmentation, sFragContent) VALUES (%s);' % ','.join(param)
        #print sql
        conn.execute(sql, ins_list)
        conn.commit()

    if len(allLevels) == 0:

      # The LTS has no levels defined

      logicalTableFileName  = baseDir + ltsXmlFile.getroot().attrib['logicalTableRef'].split('#')[0]
      subjectAreaRef        = ET.parse(logicalTableFileName).getroot().attrib['subjectAreaRef']
      bm                    = getBusinessModel(subjectAreaRef)


      lts_out.write(template % (lTableName, ltsName.replace('"',''), bm, "", ""))
      ins_line = '%s||||%s||||%s||||%s||||%s||||%s||||%s||||%s||||%s' % (lTable[3], bm, lTableName, ltsName, "", "", contentFilter, canCombine, fragmentContent)
      ins_list =  ins_line.split('||||')
      #print len(ins_list)
      
      param = ['?' for item in ins_list ]
      sql = 'INSERT INTO ltslevels (sXmlFileName, sBusinessModel, sLogicalTable, sLogicalTableSource, sDimension, sLevel, sContentFilter, sFragmentation, sFragContent) VALUES (%s);' % ','.join(param)
      #print sql
      conn.execute(sql, ins_list)
      conn.commit()
  
    # Print all the columns in the Logical Table Source
    if '--COLUMNS' in sys.argv: print_all_columns(ltsXmlFile)
  
  lts_out.close()
  
if __name__ == '__main__':
  __version__ = "0.5"
  print_banner()
  conn = sqlite3.connect('temp.db')
  conn.execute('drop table if exists ltslevels')
  conn.execute('CREATE TABLE LTSLEVELS ( sXmlFileName TEXT, sBusinessModel TEXT, sLogicalTable TEXT, sLogicalTableSource TEXT, sDimension TEXT, sLevel TEXT, sContentFilter TEXT, sFragmentation TEXT, sFragContent TEXT )')
  conn.execute('drop view if exists vw_lts')
  conn.execute('CREATE VIEW "vw_lts" AS select sXmlFileName xmlFile, sBusinessModel bm, sLogicalTable lt, sLogicalTableSource lts,  sDimension dim, sLevel lvl, sContentFilter cf, sFragmentation fr, sFragContent fc from ltslevels')
  main()
  print_report()
  conn.close()

