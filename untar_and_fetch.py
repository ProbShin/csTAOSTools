#!/usr/bin/env python3
#import io
import os
import multiprocessing
import subprocess
import sys
import threading
import traceback
import concurrent.futures

# target to collect, will be used as regex
TARGET_FILES="""
process.h .*create.*\.c
startcpumeasure.c, resched.c, clkhandler.c, clkinit.c,  sleep.c, proccpuuse.c
"""



# The number of concurrent workers equals the number of CPU threads.
NUM_WORKERS = multiprocessing.cpu_count()


class Colors:
    DEFAULT = "\x1B[0m"
    RED = "\x1B[31m"
    GREEN = "\x1B[32m"
    YELLOW = "\x1B[33m"
    BLUE = "\x1B[34m"
    MAGENTA = "\x1B[35m"
    CYAN = "\x1B[36m"
    WHITE = "\x1B[37m"



def extract_single_gzip(s):
    student = s[:-2]
    path = "./misc/"+student
    tarball = path+"/"+s
    #if s[0:2]=="az":
    #    raise Exception("wocao")
    os.makedirs(path, exist_ok=True)
    os.rename(s, tarball)
    subprocess.run(["tar", "-xf", tarball, "-C", path])
    return


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
    print(Colors.MAGENTA+"extract done (into %s/misc/ folder"%os.getcwd()+Colors.DEFAULT)
    print("Success: %d / %d"%(num_success, len(submission)))
    if failed:
        print("Failures:")
        for e in sorted(failed):
            print(" %s : %s"%e)
    return


def collect_per_student(student, targets):
    src_path = './misc/'+student
    dst_path = './moss/'+student
    os.makedirs(dst_path, exist_ok=True)
    warning = ""
    for t in targets:
        p = subprocess.Popen(["find", src_path, "-type", "f", "-regex", ".*/"+t], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out,err)=p.communicate()
        found = out.decode().strip().split()
        if not found:
            warning += " %s"%t
        else:
            for f in found:
                os.rename(f, dst_path+"/"+f[f.rfind("/")+1:])
    if warning:
        raise Exception("cannot find '%s'"%warning)
    return

def collect_targets(targets):
    warning=[]
    students = os.listdir('./misc')
    print("-"*50)
    print(Colors.MAGENTA+"start collect, find %d students folders under "%len(students) + Colors.YELLOW+"'%s/misc/'"%os.getcwd()+Colors.DEFAULT)
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(collect_per_student, s, targets):s for s in students }
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                warning.append((futures[future], str(e)))
    print(Colors.MAGENTA+"collected result stored in "+Colors.YELLOW+"'%s'"%(os.getcwd()+"/moss/")+Colors.DEFAULT)
    if warning:
        for e in sorted(warning):
            print(Colors.RED + " %s : %s"%e+Colors.DEFAULT)

    return

def main(args):
    if len(args) != 2:
        print(Colors.RED + "Usage: %s turnin_path" % args[0] + Colors.DEFAULT, file=sys.stderr)
        sys.exit(1)
    elif not os.path.isdir(args[1]):
        print(Colors.RED + "Error: \"%s\" is not a valid path." % args[1] + Colors.DEFAULT, file=sys.stderr)
        sys.exit(1)
    print(Colors.MAGENTA + 'Running %d threads in parallel...' % NUM_WORKERS + Colors.DEFAULT)

    path = args[1]
    os.chdir(path)

    extract_gzip_files()
    collect_targets(TARGET_FILES.strip().replace(","," ").split())
    return


if __name__ == '__main__':
    main(sys.argv)

