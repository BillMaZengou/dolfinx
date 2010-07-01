#!/usr/bin/env python

import os
import boost

from commonPkgConfigUtils import *

def getArmadilloDir(sconsEnv=None):
    return getPackageDir("armadillo", sconsEnv=sconsEnv, default="/usr")

def pkgVersion(compiler=None, linker=None,
               cflags=None, libs=None, sconsEnv=None):
    """Return Armadillo version."""
    if not compiler:
        compiler = get_compiler(sconsEnv)
    if not linker:
        linker = get_linker(sconsEnv)
    if not cflags:
        cflags = pkgCflags(sconsEnv=sconsEnv)
    if not libs:
        libs = pkgLibs(sconsEnv=sconsEnv)

    cpp_version_str = r"""
#include "armadillo"
#include <iostream>
using namespace arma;
int main() {
  std::cout << arma_version::major << std::endl;
  std::cout << arma_version::minor << std::endl;
  std::cout << arma_version::patch << std::endl;
  return 0;
}
"""
    cpp_file = "armadillo_config_test_version.cpp"
    write_cppfile(cpp_version_str, cpp_file)

    cmdstr = "%s -o a.out %s %s %s %s" % \
           (linker, cflags, boost.pkgCflags(sconsEnv=sconsEnv), libs, cpp_file)
    linkFailed, cmdoutput = getstatusoutput(cmdstr)
    if linkFailed:
        remove_cppfile(cpp_file)
        raise UnableToLinkException("Armadillo", cmd=cmdstr,
                                    program=cpp_version_str,
                                    errormsg=cmdoutput)

    cmdstr = os.path.join(os.getcwd(), "a.out")
    runFailed, cmdoutput = getstatusoutput(cmdstr)
    remove_cppfile(cpp_file, execfile=True)
    if runFailed:
        raise UnableToRunException("Armadillo", errormsg=cmdoutput)
    
    return '.'.join(cmdoutput.split())

def pkgLibs(compiler=None, linker=None, cflags=None, sconsEnv=None):
    if not compiler:
        compiler = get_compiler(sconsEnv)
    if not linker:
        linker = get_linker(sconsEnv)
    if not cflags:
        cflags = pkgCflags(sconsEnv=sconsEnv)

    cpp_test_libs_str = r"""
#include <armadillo>

int main()
{
 arma::mat A = arma::rand(4,4);
 arma::vec b = arma::rand(4);
 arma::vec x = arma::solve(A, b);

 return 0;
}
"""
    cpp_file = "armadillo_config_test_libs.cpp"
    write_cppfile(cpp_test_libs_str, cpp_file)

    # test that we can compile
    cmdstr = "%s -c %s %s %s" % \
             (compiler, cflags, boost.pkgCflags(sconsEnv=sconsEnv), cpp_file)
    compileFailed, cmdoutput = getstatusoutput(cmdstr)
    if compileFailed:
        remove_cppfile(cpp_file)
        raise UnableToCompileException("Armadillo", cmd=cmdstr,
                                       program=cpp_test_libs_str,
                                       errormsg=cmdoutput)

    # test that we can link
    # the Armadillo library is usually either in $ARMADILLO_DIR/lib or
    # $ARMADILLO_DIR/lib64 (on 64 bits platforms)
    for lib_dir in ("lib", "lib64"):
        libs = "-L%s -larmadillo" % \
               os.path.join(getArmadilloDir(sconsEnv=sconsEnv), lib_dir)
        if get_architecture() == "darwin":
            libs += " -framework vecLib"
        cmdstr = "%s %s -o a.out %s" % \
               (linker, cpp_file.replace('.cpp', '.o'), libs)
        linkFailed, cmdoutput = getstatusoutput(cmdstr)
        if linkFailed:
            # try adding -lgfortran to get around Hardy libatlas-base-dev issue
            libs += " -lgfortran" 
            cmdstr = "%s %s -o a.out %s" % \
                     (linker, cpp_file.replace('.cpp', '.o'), libs)
            linkFailed, cmdoutput = getstatusoutput(cmdstr)
            if not linkFailed:
                break
        else:
            break
    if linkFailed:
        remove_cppfile(cpp_file, ofile=True)
        raise UnableToLinkException("Armadillo", cmd=cmdstr,
                                     program=cpp_test_libs_str,
                                     errormsg=cmdoutput)

    # test that we can run the binary
    armadillo_lib_dir = \
            os.path.join(getArmadilloDir(sconsEnv=sconsEnv), lib_dir)
    if get_architecture() == 'darwin':
        os.putenv('DYLD_LIBRARY_PATH',
                  os.pathsep.join([armadillo_lib_dir,
                                   os.getenv('DYLD_LIBRARY_PATH', '')]))
    else:
        os.putenv('LD_LIBRARY_PATH',
                  os.pathsep.join([armadillo_lib_dir,
                                   os.getenv('LD_LIBRARY_PATH', '')]))
    cmdstr = os.path.join(os.getcwd(), "a.out")
    runFailed, cmdoutput = getstatusoutput(cmdstr)
    remove_cppfile(cpp_file, ofile=True, execfile=True)
    if runFailed:
        raise UnableToRunException("Armadillo", errormsg=cmdoutput)

    return libs

def pkgCflags(sconsEnv=None):
    return "-I%s" % os.path.join(getArmadilloDir(sconsEnv=sconsEnv), "include")

def pkgTests(forceCompiler=None, sconsEnv=None,
             cflags=None, libs=None, version=None, **kwargs):
    """Run the tests for this package.
     
    If Ok, return various variables, if not we will end with an exception.
    forceCompiler, if set, should be a tuple containing (compiler, linker)
    or just a string, which in that case will be used as both
    """
    # set which compiler and linker to use:
    if not forceCompiler:
        compiler = get_compiler(sconsEnv)
        linker = get_linker(sconsEnv)
    else:
        compiler, linker = set_forced_compiler(forceCompiler)

    if not cflags:
        cflags = pkgCflags(sconsEnv=sconsEnv)
    if not libs:
        libs = pkgLibs(compiler=compiler, linker=linker,
                       cflags=cflags, sconsEnv=sconsEnv)
    else:
        pkgLibs(compiler=compiler, linker=linker,
                cflags=cflags, sconsEnv=sconsEnv)
    if not version:
        version = pkgVersion(compiler=compiler, linker=linker,
                             cflags=cflags, libs=libs, sconsEnv=sconsEnv)

    return version, libs, cflags

def generatePkgConf(directory=None, sconsEnv=None, **kwargs):
    if directory is None:
        directory = suitablePkgConfDir()

    # armadillo.pc requires boost.pc so make sure it is available
    dep_module_header_and_libs('Boost', 'boost', sconsEnv=sconsEnv)

    version, libs, cflags = pkgTests(sconsEnv=sconsEnv)

    pkg_file_str = r"""Name: Armadillo
Version: %s
Description: streamlined C++ linear algebra library
Requires: boost
Libs: %s
Cflags: %s
""" % (version, libs, repr(cflags)[1:-1])
    # FIXME:            ^^^^^^^^^^^^^^^^^^
    # Is there a better way to handle this on Windows?
  
    pkg_file = open(os.path.join(directory, "armadillo.pc"), 'w')
    pkg_file.write(pkg_file_str)
    pkg_file.close()
    print "done\n Found Armadillo and generated pkg-config file in\n '%s'" % \
          directory

if __name__ == "__main__":
  generatePkgConf(directory=".")
