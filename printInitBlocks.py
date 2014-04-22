#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  printInitBlocks.py
#  
#  Copyright 2013 Phil D'Amico <phil.damico@oracle.com>
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  

import re
import datetime
import sys
import os
import xml.etree.ElementTree as ET

def print_banner(theRootDir=''):

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
  ctime = datetime.datetime.strftime(datetime.datetime.now(), "%b %d, %Y %I:%M %p")
  print ctime.center(banner_width)
  print theRootDir.center(banner_width)
  print '-'*banner_width + '\n'


def main():

  rpd       = '{http://www.oracle.com/obis/repository}'
  
  if len(sys.argv)>1 : 
    rootDir = sys.argv[1]
    if rootDir.strip()[-1] == '/' : rootDir = rootDir.strip()[:-1]
  else:
    rootDir   = '/home/pdamico/Desktop/sampleapp'

  os.chdir(rootDir + '/oracle/bi/server/base/InitBlock')
  
  print_banner(rootDir)
  lstInitBlocks = []
  
  for ibFileName in os.listdir('.'):
    
    # this is the format string used to print out all the values
    # e.g. "print template % (string01, string02)

    template = '%s%20s: %s'
    
    # parse the xml file

    ibAsXml      = ET.parse(ibFileName)
    
    # get all the attributes of the root element

    ibRoot       = ibAsXml.getroot().attrib
    
    # Set some defaults, in case the attributes aren't present in the 
    # root element
    
    isSessionVar  = 'Repository'

    refreshPeriod = ''

    name = ''
    
    isEnabled = 'true'
    
    if 'isSessionVar' in ibRoot : 
      if ibRoot['isSessionVar']=='true': isSessionVar = 'Session'
    
    if 'name' in ibRoot : name = ibRoot['name']

    if 'isEnabled' in ibRoot : isEnabled = ibRoot['isEnabled']

    if 'refreshPeriod' in ibRoot: refreshPeriod = ibRoot['refreshPeriod']
    
    varSql = ''
    
    if ibAsXml.find('.//{0}DBMapItem/{0}Value'.format(rpd)) \
      is not None and \
      ibAsXml.find('.//{0}DBMapItem/{0}Value'.format(rpd)).text \
      is not None:
      
      varSql = ibAsXml.find('.//{0}DBMapItem/{0}Value'.format(rpd)).text
    

    # Now we're going to determine what Variables this InitBlock
    # Sets. 

    varSets       = []

    if len(ibAsXml.findall('.//{0}RefVariables'.format(rpd)))>0:

      for varSet in ibAsXml.findall('.//{0}RefVariable'.format(rpd)):

        aVariable = varSet.attrib['variableRef']

        variableXml   = ET.parse('..' + aVariable.partition('/base')[2].split('#')[0])

        variableName  = variableXml.getroot().attrib['name']

        varSets.append(variableName)

    isRowWiseInit = 'No'
    if 'isRowWiseInit' in ibRoot : 
      if ibRoot['isRowWiseInit']=='true': isRowWiseInit = 'Yes'
    
    varDescription = ''
    if ibAsXml.find('.//{0}Description'.format(rpd)) is not None:
      if ibAsXml.find('.//{0}Description'.format(rpd)).text is not None:
        varDescription = ibAsXml.find('.//{0}Description'.format(rpd)).text

    

    precedentInitBlocks=[]
    
    if len(ibAsXml.findall('.//{0}RefPredecessors/{0}RefInitBlock'.format(rpd))) > 0:
        for precInitBlock in  ibAsXml.findall('.//{0}RefPredecessors/{0}RefInitBlock'.format(rpd)):
            ibName = ET.parse(rootDir + precInitBlock.attrib['predecessorRef'].split('#')[0]).getroot().attrib['name']
            precedentInitBlocks.append(ibName)

    # Get the fully-qualified Connection Pool Names, if any. 
    # This is in two parts:
    # [Database].[Connection Pool Name]

    dbName = ''

    cpName = ''

    if 'connectionPoolRef' in ibAsXml.getroot().attrib:

      cpRef   = ibAsXml.getroot().attrib['connectionPoolRef']
      cpXml   = ET.parse('..' + cpRef.partition('/base')[2].split('#')[0])
      cpName  = cpXml.getroot().attrib['name']
    
      if 'databaseRef' in cpXml.getroot().attrib:

        dbRef   = cpXml.getroot().attrib['databaseRef']
        dbXml   = ET.parse('..' + dbRef.partition('/base')[2].split('#')[0])
        dbName  = dbXml.getroot().attrib['name']
    
    # Fully-qualified Connection Pool Name, properly formatted for 
    # printing
    
    fqCpName = ('"%s"."%s"') % (dbName, cpName)

    lstInitBlocks.append([\
        name, \
        isSessionVar, \
        refreshPeriod, \
        varSql, \
        varSets, \
        isRowWiseInit, \
        varDescription, \
        fqCpName, \
        ibFileName, \
        precedentInitBlocks, \
        isEnabled])

  # Sort the list of Initialization Blocks by type ('Session' or 'Repository') and name
  
  lstInitBlocks.sort(key=lambda v: v[1]+v[0])
  
  currentVarType = ''
  template      = '%s\t%-16s: %s'

  for varForPrinting in lstInitBlocks:

    '''
    Here is the order of the items in the list "varForPrinting"

       0  Variable Name
       1  Type (Session/Repository)
       2  Refresh Period
       3  SQL Issued (if any)
       4  Variables set (this is a list)
       5  Is this variable created via 
          "Row-wise Initialization" (Yes/No)      
       6  A free-form description (if any)
       7  The name of the connection pool used by this initialization
          block (if any)
       8  The xml file name (this is in the /InitBlock directory
          of the MDS XML Document)
       9  The names of any variables that must be initialized 
          before this one (Execution Precedence)
       10 isEnabled (true | false) 
      
    '''
    
    if currentVarType <> varForPrinting[1]:
      print '\n'
      print '-'*70
      print (varForPrinting[1] + ' Initialization Blocks').center(70)
      print '-'*70
      currentVarType = varForPrinting[1]
    #print '\t' + '-'*70

    #print template % ('', 'name', varForPrinting[0])
    print '-'*70
    print varForPrinting[0]
    print '-'*70

    print template % ('', 'type', varForPrinting[1])
    
    print template % ('', 'Enabled', varForPrinting[10])

    if varForPrinting[3] <> '':
      try:
        finalSql = ET.fromstring(varForPrinting[3]).tag
      except:
        finalSql = varForPrinting[3].replace('\n', ' ').replace('\t',' ')
        finalSql = re.sub(r'\ {2,}', ' ', finalSql)
      print template % ('', 'sql', finalSql)
    
    if varForPrinting[5] == 'Yes':
      print template % ('', 'row-wise init', varForPrinting[5])
      

    
    refreshRate = ''
    if varForPrinting[1] == 'Repository':
      refreshRate =  int(varForPrinting[2])
      if refreshRate >= 1440: 
        print template % ('', 'Refresh (days)', str(1.0 * refreshRate / 1440 ))
      else:
        print template % ('', 'Refresh (min)', str(1.0 * refreshRate) / 60 )
      
    if len(varForPrinting[6])>0:
      print template % ('', 'Description', varForPrinting[6].replace('\n', ' '))
    
    if varForPrinting[7] <> '':
      print template % ('', 'Connection Pool', varForPrinting[7].replace('\n', ' '))

    print template % ('', 'XML File Name', varForPrinting[8])
    
    if len(varForPrinting[9])>0:
        print template % ('', 'Precedence', str(varForPrinting[9]).replace('[','').replace(']',''))
        
    if len(varForPrinting[4])>0:

      for aVariable in varForPrinting[4]:
        print template % ('', 'variable set', aVariable)

    init_out.write( '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % \
                    ( \
                      varForPrinting[0], \
                      varForPrinting[10], \
                      varForPrinting[1], \
                      varForPrinting[5], \
                      str(varForPrinting[4]).replace('[','').replace(']','').replace("'",''), \
                      varForPrinting[7], \
                      finalSql, \
                      refreshRate, \
                      varForPrinting[6].replace('\n', ' ').replace('\t','')
                    )
                  )


if __name__ == '__main__':
	
  __version__ = "0.5"

  rpd       = '{http://www.oracle.com/obis/repository}'

  if len(sys.argv)>1 : 

    rootDir = sys.argv[1]

    if rootDir.strip()[-1] == '/' : rootDir = rootDir.strip()[:-1]

  else:

    rootDir   = os.getcwd()

  if not os.path.isdir(rootDir + '/oracle/bi/server/base/InitBlock'):
    print 'No Directory: %s' % (rootDir + '/oracle/bi/server/base/InitBlock')
    sys.exit()

  initCsvFileName = rootDir.split('/')[-1] + '.inits.csv'

  init_out = open(initCsvFileName, 'w')

  init_out.write( '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % \
                  ( \
                    "Name", \
                    "Enabled", \
                    "Type", \
                    "RowWise", \
                    "VariablesSet", \
                    "ConnectionPool", \
                    "SQL", \
                    "RefreshRate", \
                    "Description" 
                  )
                )
  
  main()
  
  init_out.close()
