#!/usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
#
# Copyright (C) 2007 Jamie Strandboge <jamie@ubuntu.com>
#
#    ufw is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published
#    by the Free Software Foundation; either version 2 of the License,
#    or (at your option) any later version.
#
#    ufw is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with ufw; if not, write to the Free Software Foundation,
#    Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
###########################################################################

import sys
import os.path
import os
from popen2 import Popen3
import py_compile

appname = "ufw"

# This is the prefix directory where the application will be installed.
prefixDir = os.path.join("usr", "local")
configDir = os.path.join("etc")
destDir   = os.path.join("/")
buildDir  = "./build"

# Determines if python source files are only compiled and not installed
compileOnly = False

def recursive_rm(dirPath):
    '''recursively remove directory'''
    names = os.listdir(dirPath)
    for name in names:
        path = os.path.join(dirPath, name)
        if not os.path.isdir(path):
            os.unlink(path)
        else:
            recursive_rm(path)
    os.rmdir(dirPath)

def doImportCheck():
    """ Checks for installed packages which are needed in order to run
    the application.  Gives only a warning for missing packages.
    """
    
    #print "Check for preinstalled modules:\n"
    # Check for python-foo
    # try:
    #    import foo
    #    vString = "0.1"
    #    print "python-foo is installed..."
    #    print "\tInstalled version: " + foo.__version__
    #    print "\tMinimum version: " + vString
    #    print ""
    #except ImportError:
    #    print """ERROR: python-foo not installed!!!
#You can get the module here: http://www.example.com
#"""
    #print ""

###############################################################################

def doChecks():
    """Checks if prefix directory exists. After that compile and install. 
    Installation fails if prefix directory doesn't exist.
    """

    if not os.path.exists(destDir):
        print "Destination directory does not exist!"
        sys.exit(1)

    installDir = os.path.join(destDir, os.path.basename(prefixDir))
    if not os.path.exists(installDir):
	print "Prefix directory does not exist!"
	sys.exit(1)

    installDir = os.path.join(destDir, os.path.basename(configDir))
    if not os.path.exists(installDir):
	print "Configuration directory does not exist!"
	sys.exit(1)

###############################################################################

def installManpage(f, section):
    abs = os.path.join(buildDir, "share/man/man" + section)
    if not os.path.exists(abs):
        os.makedirs(abs)
    abs = os.path.join(abs, f)
    a = Popen3("cp -f ./" + f + " " + abs)
    while a.poll() == -1:
        pass
    if a.poll() > 0:
        raise OSError("Error!!! Could not copy man page. Maybe wrong permissions?")

    print "Updating " + abs + " to use " + configDir
    a = Popen3("sed -i 's%#CONFIG_PREFIX#%" + configDir + "%' " + abs)
    while a.poll() == -1:
        pass
    if a.poll() > 0:
        raise OSError("Error!!! Could not update File. Maybe wrong permissions?")

def installBin(f, dir):
    abs = os.path.join(buildDir, dir)
    if not os.path.exists(abs):
        os.makedirs(abs)
    abs = os.path.join(abs, f)
    
    a = Popen3("cp -f ./" + f + " " + abs)
    while a.poll() == -1:
        pass
    if a.poll() > 0:
        raise OSError("Error!!! Could not copy File. Maybe wrong permissions?")

    print "Updating " + abs + " to use " + configDir
    a = Popen3("sed -i 's%#CONFIG_PREFIX#%" + configDir + "%' " + abs)
    while a.poll() == -1:
        pass
    if a.poll() > 0:
        raise OSError("Error!!! Could not update File. Maybe wrong permissions?")


def doInstall():
    """Installs compiled sourcefiles to the installation directory."""
    print "Copy program files...\n"
    if os.path.isdir(buildDir):
        recursive_rm(buildDir)
    os.mkdir(buildDir)
    
    try:
        # install binaries, libs and manpages
        for bin in [appname]:
            installBin(bin, "sbin")
	    installManpage(bin + ".8", "8")

	installDir = prefixDir
	if destDir != "/":
            installDir = os.path.join(destDir, os.path.basename(prefixDir))
        filenames = os.listdir(buildDir)
        for n in filenames:
            a = Popen3("cp -fR " + os.path.join(buildDir, n) + " " + installDir)
            while a.poll() == -1:
                pass
            if a.poll() > 0:
                raise OSError("Error!!! Could not copy File. Maybe wrong permissions?")
                
        # install etc
	installDir = configDir
	if destDir != "/":
		installDir = os.path.join(destDir, os.path.basename(configDir))
        a = Popen3("cp -fR etc/*" + " " + installDir)
        while a.poll() == -1:
            pass
        if a.poll() > 0:
            raise OSError("Error!!! Could not copy File. Maybe wrong permissions?")
		
        print "Finished copying program files.\n"
        print "Installation successful! :)"
        recursive_rm(buildDir)
        
    except OSError, errorMessage:
        print errorMessage
        recursive_rm(buildDir)
        sys.exit(1)
    except:
        raise
    
###############################################################################

def printHelp():
    """Prints a help text for the the application installation program.
    """
    
    helpString = """Install options:
 --prefix=PATH \t\t Install path (default is /usr/local)
 --config-prefix=PATH \t\t Configuration path (default is /etc)
 --destdir=PATH \t\t Install into this directory instead of '/'
 --compile-only \t Just compile source files. No installation.
 \n"""
 
    print helpString
    
    sys.exit(1)
    
###############################################################################
    
def doCompile():
    """Compiles all source files to python bytecode.
    """
    
    print "Compiling python source files ... TODO\n"

#    input, output = os.popen2("find ./lib -name \"*.py\"")
#    tmpArray = output.readlines()
#    fileList = []
#    for x in tmpArray:
#        if x[:26] == "./lib/" + appname + "/":
#            fileList.append(x[:-1])
#    for x in fileList:
#        print "compiling " + x
#        py_compile.compile(x)
        
#    print "\nFinished compiling.\n"
         
###############################################################################

def evalArguments():
    """ Evaluate options given to the install script by the user.
    """
    
    if len(sys.argv) == 2:
        printHelp()
        return
        
    for x in sys.argv[1:]:
        if x == "--compile-only":
            global compileOnly
            compileOnly = True
        elif x[:9] == "--prefix=":
            global prefixDir
            prefixDir = x[9:]
            if (prefixDir[-1] == "/") and (len(prefixDir) > 1):
                prefixDir = prefixDir[:-1]
        elif x[:16] == "--config-prefix=":
            global configDir
            configDir = x[16:]
            if (configDir[-1] == "/") and (len(configDir) > 1):
                configDir = configDir[:-1]
        elif x[:10] == "--destdir=":
            global destDir
            destDir = x[10:]
            if (destDir[-1] == "/") and (len(destDir) > 1):
                destDir = destDir[:-1]
        else:
            print "Unknown options. Exiting..."
            sys.exit(1)

###############################################################################


print appname + " (C) 2007 Jamie Strandboge\n"

doImportCheck()
evalArguments()
doChecks()
doCompile()

if not compileOnly:
    # Check if prefixDir exists
    if not(os.path.exists(prefixDir)):
        print "Prefix directory does not exist!"
        sys.exit(1)

    if not(os.path.exists(configDir)):
        print "Configuration directory does not exist!"
        sys.exit(1)

    doInstall()

