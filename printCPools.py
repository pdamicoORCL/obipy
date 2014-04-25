#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  printCpools.py
#  
#  Copyright 2013 Phil D'Amico
#  
#  

import datetime
import sys
import os
import xml.etree.ElementTree as ET


def getDatabase(theRef, baseDir):

  rpd       = '{http://www.oracle.com/obis/repository}'

  dbRef       = theRef.replace('"','').strip()
  refPath     = theRef.split('#')[0]
  refFile     = baseDir + refPath
  refXml      = ET.parse(refFile)

  objectType  = refXml.getroot().tag.replace(rpd,'')

  return refXml.getroot().attrib['name']

def build_the_list_of_ConnectionPools():
  lstConnectionPools = []

  for pTable in os.listdir('.'):
    
    
    cpool = {}
    pXml          = ET.parse(pTable)
    dbName        = getDatabase(pXml.getroot().attrib['databaseRef'], rootDir)
    dbType        = ET.parse(
                              rootDir + \
                              (
                              pXml.getroot().attrib['databaseRef'].\
                              replace('"','').\
                              strip().\

                              split('#')[0]\
                              )
                            ).getroot().attrib['type']
    cpName        = pXml.getroot().attrib['name']
    
    cpool['user'] = ''
    cpool['poolType'] = ''
    cpool['dataSource']=''
    cpool['maxConn']=''
    
    cpool['database']     = dbName
    cpool['name']         = cpName
    cpool['dbType']       = dbType

    if 'dataSource' in pXml.getroot().attrib:
      cpool['dataSource']   = pXml.getroot().attrib['dataSource']
    if 'maxConn' in pXml.getroot().attrib:
      cpool['maxConn']   = pXml.getroot().attrib['maxConn']
    if 'user' in pXml.getroot().attrib:
      cpool['user']         = pXml.getroot().attrib['user']
    if 'type' in pXml.getroot().attrib:
      cpool['poolType']         = pXml.getroot().attrib['type']
    cpool['filename']     = pTable
    
    lstConnectionPools.append(cpool)
  
  lstConnectionPools.sort(key=lambda v: v['database'] + v['name'])
  return lstConnectionPools
  

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


def main():
  

  '''
  '''  

  allConnectionPools = build_the_list_of_ConnectionPools()

  for connectionPool in allConnectionPools:
    template = '%19s: %s'
    print '-'*70
    print '"%s"."%s"' % (connectionPool['database'], connectionPool['name'])
    print '-'*70
    print template % ('dataSource', connectionPool['dataSource'])
    print template % ('user', connectionPool['user'])
    print template % ('Pool type', connectionPool['poolType'])
    print template % ('DB type', connectionPool['dbType'])
    print template % ('Max Connections', connectionPool['maxConn'])


    pool_out.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % ( \
      connectionPool['database'], \
      connectionPool['name'], \
      connectionPool['poolType'],
      connectionPool['dbType'],
      connectionPool['user'], \
      connectionPool['dataSource'], \
      connectionPool['maxConn'] \
                  ))

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
  
  if not os.path.isdir(rootDir + '/oracle/bi/server/base/ConnectionPool'):

    print 'No Directory: %s' % (rootDir + '/oracle/bi/server/base/ConnectionPool')

    sys.exit()
  


  poolCsvFileName = rootDir.split('/')[-1] + '.pools.csv'

  pool_out = open(poolCsvFileName, 'w')

  #pool_out.write("db1\tpc1\tsc1\tph1\tdb2\tpc2\tsc2\tph2\ttheJoin\n")
  pool_out.write("database\tconnectionPool\tcpType\tdbType\tuser\tdataSource\tmaxConn\n")
  
  os.chdir(rootDir + '/oracle/bi/server/base/ConnectionPool')

  main()

  pool_out.close()

  print ''
  print '\n\nOutput file: %s\n\n' % poolCsvFileName
