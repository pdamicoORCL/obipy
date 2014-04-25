#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  printJoins.py
#  
#  Copyright 2013 Phil D'Amico 
#  
#  
#  

import datetime
import sys
import os
import xml.etree.ElementTree as ET


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
  ctime = datetime.datetime.strftime(datetime.datetime.now(), "%b %d, %Y %I:%M %p")
  print ctime.center(banner_width)
  print '-'*banner_width + '\n'




def fred():
  rpd       = '{http://www.oracle.com/obis/repository}'

  
  if len(sys.argv)>1 : 
    rootDir = sys.argv[1]
    if rootDir.strip()[-1] == '/' : rootDir = rootDir.strip()[:-1]
  else:
    rootDir   = '/home/pdamico/Desktop/sampleapp'
  
  os.chdir(rootDir + '/oracle/bi/server/base/PhysicalTable')
  
  lstOfPhysicalTables = []

  for pTable in os.listdir('.'):
    
    
    pXml          = ET.parse(pTable)

    if len(pXml.findall('.//{0}PhysicalForeignKey'.format(rpd)))>0:

      pTableName    = pXml.getroot().attrib['name']

      pSchemaRef    = pXml.getroot().attrib['containerRef']

      pSchemaXml    = ET.parse('..' + pSchemaRef.partition('/base')[2].split('#')[0])
      
      pSchemaName   = pSchemaXml.getroot().attrib['name']
      
      pDbName = "****"
      
      if 'containerRef' in pSchemaXml.getroot().attrib:

        pDbRef    = pSchemaXml.getroot().attrib['containerRef']

        pDbXml    = ET.parse('..' + pDbRef.partition('/base')[2].split('#')[0])

        pDbName   = pDbXml.getroot().attrib['name']
    
      fqKey = pDbName + pSchemaName + pTableName

      #print fqKey
      lstOfPhysicalTables.append([fqKey, pTable])

  lstOfPhysicalTables.sort(key = lambda v: v[0])
  
  #print lstOfPhysicalTables
  
  #for phyTableFileName in os.listdir('.'):
  for phyTableFileName in lstOfPhysicalTables:
  
    physTableAsXml = ET.parse(phyTableFileName[1])

    
    # What is the schema Name?
    
    schemaRef =     physTableAsXml.getroot().attrib['containerRef']

    schemaXml = ET.parse('..' + schemaRef.partition('/base')[2].split('#')[0])

    schemaName = schemaXml.getroot().attrib['name']
    
    
    
    # Is this an alias?
    
    thisAliasName = ''
    
    if 'sourceTableRef' in physTableAsXml.getroot().attrib:

      thisAliasRef         = physTableAsXml.getroot().attrib['sourceTableRef']

      thisAliasXml         = ET.parse('..' + thisAliasRef.partition('/base')[2].split('#')[0])

      thisAliasName = thisAliasXml.getroot().attrib['name']

    
    # What is the database Name?
    
    thisDbName = "****"
    
    if 'containerRef' in schemaXml.getroot().attrib:

      thisDbRef         = schemaXml.getroot().attrib['containerRef']

      thisDbXml         = ET.parse('..' + thisDbRef.partition('/base')[2].split('#')[0])

      thisDbName = thisDbXml.getroot().attrib['name']

    
    # Are there any foreign Keys?
    
    if len(physTableAsXml.findall('.//{0}PhysicalForeignKey'.format(rpd)))>0:

      physTableName = physTableAsXml.getroot().attrib['name']

      print ''
      
      # If this is an alias, the line we print is slightly different
      
      if thisAliasName == '': 
        print '"%s"."%s"."%s"' % (thisDbName, schemaName, physTableName)
      else:
        print '"%s"."%s"."%s"\t[ Alias of: %s ]' % (thisDbName, schemaName, physTableName, thisAliasName)

      # Look through all the foreign keys
      
      for aJoin in physTableAsXml.findall('.//{0}PhysicalForeignKey'.format(rpd)):

        # print aJoin.attrib['counterPartKeyRef']

        otherTableRef   = aJoin.attrib['counterPartKeyRef']

        otherTable      = ET.parse('..' + otherTableRef.partition('/base')[2].split('#')[0])
        

        thisAliasName = ''
        
        if 'sourceTableRef' in otherTable.getroot().attrib:

          thisAliasRef         = otherTable.getroot().attrib['sourceTableRef']

          thisAliasXml         = ET.parse('..' + thisAliasRef.partition('/base')[2].split('#')[0])

          thisAliasName = thisAliasXml.getroot().attrib['name']


        othSchemaRef  = otherTable.getroot().attrib['containerRef']

        othSchemaXml  = ET.parse('..' + othSchemaRef.partition('/base')[2].split('#')[0])

        othSchemaName = othSchemaXml.getroot().attrib['name']
        
        dbName = '****'
        
        if 'containerRef' in othSchemaXml.getroot().attrib:

          dbRef         = othSchemaXml.getroot().attrib['containerRef']

          dbXml         = ET.parse('..' + dbRef.partition('/base')[2].split('#')[0])

          dbName = dbXml.getroot().attrib['name']

        if dbName == thisDbName and othSchemaName == schemaName:
          if thisAliasName == '':
            print '\t"%s"' % (otherTable.getroot().attrib['name'])
          else:
            print '\t"%s"\t[ Alias of: %s ]' % (otherTable.getroot().attrib['name'], thisAliasName)
        else:
          if thisAliasName == '':
            print '\t"%s"."%s"."%s"' % (dbName, othSchemaName, otherTable.getroot().attrib['name'])
          else:
            print '\t"%s"."%s"."%s"\t[ Alias of: %s ]' % (dbName, othSchemaName, otherTable.getroot().attrib['name'], thisAliasName)

def main():
  
  fred()
  return 0

if __name__ == '__main__':

  __version__ = "0.5"
  
  print_banner()

  main()

