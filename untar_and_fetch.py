#!/usr/bin/env python3

__author__ = "xin cheng"

Usage=\
'''
1. extract all *.z within a given folder.  (optional)
2. collect all TARGET_FILES and put them under folder 'moss'
P.S. Thanks "xb" for his ideas.

Usage: ./untar_and_fetch.py <submit_path> [-t <TARGET_FILES>] [other options]

    <submitted_path>  : is a folder contains all students submitted .z
    -t <TARGET_FILES> : optional, indicate the files collect to moss
                        i.e. -t "create.c process.h main.c"
    --misc  <misc folder name>  : change the default misc folder name 
    --moss  <moss folder name>  : change the default moss folder name
    -h / --help       : print usage.

Demo:
$> ls lab3/
foo.z
bar.z
$> ./untar_and_fetch.py ./lab3
$> ls lab3/
moss/
 |- foo/ : contains target files
 |- boo/ : contains target files
misc
 |- foo/ : contains the tarball and its extracted files
 |- boo  : contains the tarball and its extracted files 
 
Example:
$> ./untar_and_fetch.py /lab3
$> ./untar_and_fetch.py /lab3 -t "main.c create.c send.*.c" 
'''


import os
import multiprocessing
import subprocess
import sys
import concurrent.futures


# target to collect, each element will be used as a regex pattern
TARGET_FILES="""
process.h .*create.*.c
startcpumeasure.c, resched.c, clkhandler.c,
clkinit.c,
sleep.c,
proccpuuse.c
"""
MISC_FOLDER = "./misc"
MOSS_FOLDER = "./moss"

# The number of concurrent workers equals the number of CPU threads.
NUM_WORKERS = multiprocessing.cpu_count()


def usage(app="./untar_and_fetch.py"):
    print(Usage.replace("./untar_and_fetch.py", app))
    return


'''
Terminal Color
'''
class Colors:
    DEFAULT = "\x1B[0m"
    RED = "\x1B[31m"
    GREEN = "\x1B[32m"
    YELLOW = "\x1B[33m"
    BLUE = "\x1B[34m"
    MAGENTA = "\x1B[35m"
    CYAN = "\x1B[36m"
    WHITE = "\x1B[37m"


'''
for student s, move tarball into 'misc' folder and extract
'''
def extract_single_gzip(s):
    student = s[:-2]
    path = "./%s/%s"%(MISC_FOLDER,student)
    tarball = path+"/"+s
    os.makedirs(path, exist_ok=True)
    os.rename(s, tarball)
    print("untar -xf %s -C %s"%(s, path), flush=True)
    subprocess.run(["tar", "-xf", tarball, "-C", path])
    return

'''
for each *.z file, move and extract.
'''
def extract_gzip_files():
    num_success = 0
    failed = []
    submission = [s for s in os.listdir() if s[-2:].lower()==".z"]
    print("-"*50)
    print(Colors.MAGENTA+"start extract (find %d submission under '%s')"%(len(submission), os.getcwd())+Colors.DEFAULT)
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(extract_single_gzip, s) : s for s in submission}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
                num_success += 1
            except Exception as e:
                failed.append((futures[future], str(e)))
    print(Colors.MAGENTA+"extract done (into %s/%s/ folder"%(os.getcwd(), MISC_FOLDER)+Colors.DEFAULT)
    print("Success: %d / %d"%(num_success, len(submission)))
    if failed:
        print("Failures:")
        for e in sorted(failed):
            print(" %s : %s"%e)
    return

'''
for students, collect each target files
'''
def collect_per_student(student, targets):
    src_path = './%s/%s'%(MISC_FOLDER, student)
    dst_path = './%s/%s'%(MOSS_FOLDER, student)
    os.makedirs(dst_path, exist_ok=True)
    missing_target = []
    num_find_files = 0
    for t in targets:
        p = subprocess.Popen(["find", src_path, "-type", "f", "-regex", ".*/"+t],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out,err)=p.communicate()
        found = sorted([ (f[f.rfind("/")+1:], f) for f in out.decode().strip().split() ])
        for i, (dst, src) in enumerate(found):
            while os.path.isfile(dst):
                dst = 'a'+dst
            os.rename(src, "%s/%s"%(dst_path, dst))
        if not found:
            missing_target.append(t)

    print("%s No.TargetsFind %d"%(student, num_find_files))
    if missing_target:
        raise Exception("cannot find '%s'"%(' '.join(missing_target)))
    return

'''
for all student under 'misc', find target files and move it to 'moss'
'''
def collect_targets(targets):
    warning=[]
    students = os.listdir('./%s'%MISC_FOLDER)
    print("-"*50)
    print(Colors.MAGENTA+"start collect, find %d students folders under "%len(students) \
          + Colors.YELLOW+"'%s/%s/'"%(os.getcwd(), MISC_FOLDER)+Colors.DEFAULT)
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(collect_per_student, s, targets):s for s in students }
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                warning.append((futures[future], str(e)))
    print(Colors.MAGENTA+"collected result stored in "+Colors.YELLOW+"'%s/%s/'"%(os.getcwd(), MOSS_FOLDER)+Colors.DEFAULT)
    if warning:
        for e in sorted(warning):
            print(Colors.RED + " %s : %s"%e+Colors.DEFAULT)

    return


def main(args):
    global TARGET_FILES, MISC_FOLDER, MOSS_FOLDER
    if len(args) < 2:
        usage(args[0])
        print(Colors.RED + "Usage: %s turnin_path" % args[0] + Colors.DEFAULT, file=sys.stderr)
        sys.exit(1)
    elif not os.path.isdir(args[1]):
        print(Colors.RED + "Error: \"%s\" is not a valid path." % args[1] + Colors.DEFAULT, file=sys.stderr)
        sys.exit(1)

    i = 2
    while i<len(args):
        cmd = args[i]
        i+=1
        if cmd == "-t":
            TARGET_FILES = args[i]
            i += 1
            continue
        if cmd == "--misc":
            MISC_FOLDER = args[i]
            i += 1
            continue
        if cmd == "--moss":
            MOSS_FOLDER = args[i]
            i += 1
            continue
        if cmd == "-h" or cmd == "--help":
            usage()
            sys.exit(1)
        raise Exception("unknown input parameters '%s'"%cmd)

    print(Colors.MAGENTA + 'Running %d threads in parallel...' % NUM_WORKERS + Colors.DEFAULT)
    os.chdir(args[1])
    extract_gzip_files()
    collect_targets(TARGET_FILES.strip().replace(","," ").split())
    return


if __name__ == '__main__':
    main(sys.argv)

