#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  printVars.py
#  
#  Copyright 2013 Phil D'Amico 
#  
#  

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

  # This is the namespace for all the elements in the XML files
  
  rpd       = '{http://www.oracle.com/obis/repository}'
  
  # Process the command line
  
  if len(sys.argv)>1 : 
    rootDir = sys.argv[1]
    if rootDir.strip()[-1] == '/' : rootDir = rootDir.strip()[:-1]
  else:
    rootDir   = '/home/pdamico/Desktop/sampleapp'

  # Move to the Variable directory
  os.chdir(rootDir + '/oracle/bi/server/base/Variable')
  
  # prints a banner to STDOUT
  
  print_banner(rootDir)
  
  # This will hold all the information. We build this list as we 
  # loop through all the Variable .xml files. When we're done with
  # the loop, we will sort this list by Variable Type (Repository or
  # Session) and name.
  
  lstVariables = []
  
  # loop through all the .xml files in the "Variable" directory
  
  for x in os.listdir('.'):

    varAsXml      = ET.parse(x)
    varRoot       = varAsXml.getroot().attrib
    isSessionVar  = 'Repository'
    initBlockRef  = ''
    isEnabled     = 'true'
    name          = ''
    
    if 'isSessionVar' in varRoot : 
      if varRoot['isSessionVar']=='true': isSessionVar = 'Session'

    if 'initBlockRef' in varRoot : initBlockRef = varRoot['initBlockRef']

    if 'name' in varRoot : name = varRoot['name']
    
    if 'isEnabled' in varRoot : isEnabled = varRoot['isEnabled']

    if varAsXml.find('.//{0}ExprTextDesc'.format(rpd)) is not None\
    and varAsXml.find('.//{0}ExprTextDesc'.format(rpd)).text is not None: 

      defaultValue = varAsXml.find('.//{0}ExprTextDesc'.format(rpd)).text
    
    else:
      
      defaultValue = ""
        
  
    initBlockName   = 'None'
    initBlockSql    = 'None'
  
    if 'initBlockRef' in varRoot: 

      initBlockXml = ET.parse('..' + initBlockRef.partition('/base')[2].split('#')[0])

      initBlockName = initBlockXml.getroot().attrib['name']

      if initBlockXml.find('.//{0}DBMapItem/{0}Value'.format(rpd)) is not None and \
      initBlockXml.find('.//{0}DBMapItem/{0}Value'.format(rpd)).text:

        initBlockSql = initBlockXml.find('.//{0}DBMapItem/{0}Value'.format(rpd)).text.replace('\n',' ')
    
    # Add the record to the list. When we're done with this loop - we've
    # read all the Variable .xml files - we will sort the list and print
    
    lstVariables.append([name, isSessionVar, defaultValue, initBlockName, initBlockSql, isEnabled])

  # This command sorts the list by Variable Type and Name so it will print in sorted order
  
  lstVariables.sort(key=lambda v: v[1]+v[0])
  
  # I set this variable to track the type of variable. We break and 
  # print a heading when this changes
  
  currentVarType = ''
  template      = '\t%-20s: %s'

  for var in lstVariables:

    if currentVarType <> var[1]:

      print '\n'
      print '-'*70
      print (var[1] + ' Variables').center(70)
      print '-'*70
      currentVarType = var[1]

    print '-'*70

    #print template % ('name', var[0])
    #print var[0].center(70) 
    print var[0]

    print '-'*70

    print template % ('type', var[1])

    print template % ('Enabled', var[5])

    print template % ('Default', var[2])

    print template % ('InitBlock Name', var[3])

    print template % ('InitBlock SQL', var[4])
    
	

if __name__ == '__main__':
	
  __version__ = "0.5"
  main()

