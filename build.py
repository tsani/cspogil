#!/usr/bin/env python
"""Compiles student and teacher PDFs for each LaTeX source file."""

from __future__ import print_function

import os
import shutil
import sys

# command to use for os.system
LATEX = "pdflatex -interaction=nonstopmode"

# remove temporary output files
CLEAN = True

# default course paths to build
PATHS = ["CS0", "CS1"]

def latex(name, suff, force=False):
    """Run latex and rename pdf file."""
    print("  " + suff + "...", end=' ')
    sys.stdout.flush()
    # check timestamp
    pdf = name[:-4] + "_" + suff + ".pdf"
    if not force and os.path.isfile(pdf):
        if os.path.getmtime(pdf) > os.path.getmtime(name):
            print("SKIP")
            return
    # pass suffix to latex
    cmd = LATEX + " '\\def\\" + suff + "{}\\input{_TEMP_.tex}'"
    status = os.system(cmd + " > _TEMP_1.run")
    status = os.system(cmd + " > _TEMP_2.run")
    if status == 0:
        print("OK")
        os.rename("_TEMP_.pdf", pdf)
    else:
        print("ERROR")
        return status
    # clean up temp files
    if CLEAN:
        os.remove("_TEMP_.aux")
        os.remove("_TEMP_.log")
        os.remove("_TEMP_.out")
        os.remove("_TEMP_1.run")
        os.remove("_TEMP_2.run")

def build(path, name, force=False):
    """Build the given source file."""
    if name == "_TEMP_.tex":
        return  # ignore previous build
    if path in PATHS:
        return  # ignore top-level files
    print(os.path.join(path, name))
    if "\\documentclass" in open(name).read():
        # copy original activity file
        shutil.copyfile(name, "_TEMP_.tex")
    else:
        # create activity for model
        temp = open("_TEMP_.tex", 'w')
        temp.write("\\documentclass[12pt]{article}\n")
        temp.write("\\title{}\n")
        temp.write("\\author{}\n")
        temp.write("\\date{}\n")
        temp.write("\\input{../../cspogil.sty}\n")
        temp.write("\\begin{document}\n")
        temp.write("\\input{" + name + "}\n")
        temp.write("\\end{document}\n")
        temp.close()
    # build teacher version
    status = latex(name, "Teacher", force=force)
    if status:
        return status
    # build student version
    status = latex(name, "Student", force=force)
    if status:
        return status
    # delete temp activity
    if CLEAN:
        os.remove("_TEMP_.tex")

def main(courses, pattern, force=False):
    """Find and build all files."""
    cwd = os.getcwd()
    for root in courses:
        for path, dirs, files in sorted(os.walk(root)):
            for name in files:
                # build tex files
                if pattern != "clean" and name.endswith(".tex"):
                    if pattern == "all" or pattern in name:
                        os.chdir(path)
                        status = build(path, name, force=force)
                        if status:
                            return status
                        os.chdir(cwd)
                # clean pdf files
                if pattern == "clean" and name.endswith(".pdf"):
                    if name[-12:-4] in ["_Student", "_Teacher"]:
                        pathname = os.path.join(path, name)
                        print(pathname)
                        os.remove(pathname)

if __name__ == "__main__":
    targets = PATHS
    got_targets = False
    action = "all"
    got_action = False
    force = False
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--force":
            force = True
        elif not got_targets:
            targets= [sys.argv[i]]
            got_targets = True
        elif not got_action:
            action = sys.argv[i]
            got_action = True
        else:
            print("Unexpected command line arguments.")
            print("Usage: build.py [COURSE] {all | clean | NAME}")
            print("COURSE is CS0, CS1, or blank for all")
            print("NAME is any substring of the file(s)")
            sys.exit(1)
        i += 1

    main(targets, action, force=force)
