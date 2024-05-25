#include <stdlib.h>
#include <stdio.h>

int nops();

int main(int argc, char** argv){
    int size = atoi(argv[1]);
    for(int i = 0; i < size; ++i){
        nops();
    }
    exit(0);
}