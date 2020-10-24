# csTAOSTools
collections of ta tools

## untar_and_fetch.py 
is a script to untar all students submissions and collect *target_files* by move them into a separate folder for moss check or grade.
All the tasks are done in parallel.

### usage

`./untar_and_fetch.py <submit_path> [-t <TARGET_FILES>] [other options]`

options:
    
    
    <submitted_path>  : is a folder contains all students submitted .z
    -t <TARGET_FILES> : optional, indicate the files collect to moss
                        i.e. -t "create.c process.h main.c .*lab3.*.[pP][dD][fF]"
    --misc  <misc folder name>  : change the default misc folder name 
    --moss  <moss folder name>  : change the default moss folder name
    -h / --help       : print usage.
    

### Demo:
```
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
```
 
### Example:

```
$> ./untar_and_fetch.py /lab3
$> ./untar_and_fetch.py /lab3 -t "create.c, startcpumeasure.c, resched.c, clkhandler.c, clkinit.c, process.h, sleep.c, proccpuuse.c
resched.c, clkhandler.c, create.c, sleep.c"
```

### Tips:
for `-t <TARGET_FILES>`, the TARGEST_FILES will be split() and each element will be served as regex pattern. 

Thus `-t ".*create.*c"` could match the following files
```
xinu-2020/system/create.c
myxinu/system/lfscreate.c
system/original_create_bkup.c
``` 
