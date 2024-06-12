#include <stdlib.h>
#include <stdio.h>

int fib(int n){
    if (n < 2) {
        return 1;
    }
    return fib(n-1)+fib(n-2);
}

int main(){
    int num = 45;
    printf("fib(%d)=%d\n", num, fib(num));
}