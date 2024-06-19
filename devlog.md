## TODO
* create results visualization program
* collections should statically (without collecting them) be able to determine what dependencies they have


## Notes
* need to know the line-number of each line of source code
* attempted to do this by counting lines from start of each section's annotation
* but this is unreliable:
    - there are sections starting in the middle of the source code
    - it appears some lines are skipped
* also attempted to use the numbers after the colon and before the text of the source line
    - they are highely correlated to the line-number, but are not exactly
    - some times they are constantly offset from the line number by 5, some times by 3
    - but what does this number actually indicate?
    - searches online and through manual did not yeild any useful results
    - looking through source code to try to udnerstand the purpose of this
* source code of perf annotate is in the linux repo:
    - `https://github.com/torvalds/linux/blob/master/tools/perf/builtin-annotate.c`
    - `cmd_annotate` appears to function as `main`
    - actual start of logic appears to be line 867
    - `hists__find_annotations` looks like an intresting function
* tracking the source code is too hard
* approaching from another direction:
    - how is the by-line information stored in elf?
    - can I manually check it's validity by interpreting the elf?
    - debugging info is encoded within the elf in the `dwarf` format
    - found an article on this topic: https://eli.thegreenplace.net/2011/02/07/how-debuggers-work-part-3-debugging-information
    - section titled `Looking up line numbers` is especially intresting
* took `bt.cpp` as example, `objdump --dwarf=decodedline bt.S` yielded:
    ```
    File name                            Line number    Starting address    View    Stmt
    bt.cpp                                       348              0x66e0               x
    bt.cpp                                       349              0x66e0       1       x
    bt.cpp                                       350              0x66e0       2       x
    bt.cpp                                       351              0x66e0       3
    ```
* if we look at the annotated output:
    ```
    : 3    Disassembly of section .text:
    :
    : 5    00000000000066e0 <binvcrhs(double (*) [5], double (*) [5], double*)>:
    : 6    binvcrhs(double (*) [5], double (*) [5], double*):
    : 351  }
    :
    : 353  void binvcrhs(double lhs[5][5], double c[5][5], double r[5]){
    ```
* and the source code at lines 346-348:
    ```
    }

    void binvcrhs(double lhs[5][5], double c[5][5], double r[5]){
    ```