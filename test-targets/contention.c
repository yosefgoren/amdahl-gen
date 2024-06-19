#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <omp.h>
#define NUM_ITER (0x100042)

int main(){
    size_t line_size = sysconf (_SC_LEVEL1_DCACHE_LINESIZE);
    unsigned char buf[line_size];
    memset(buf, 0, line_size);
    
    omp_set_dynamic(0);
    
    printf("line size: %lu\n", line_size);

    double start_time = omp_get_wtime();
    // int real_thread_count = 0;

    #pragma omp parallel
    {
        // #pragma atomic
        // ++real_thread_count;
        int num_threads = omp_get_num_threads();

        int tid = omp_get_thread_num();
        for(int i = 0; i < NUM_ITER; ++i) {
            for(int off = tid; off < line_size; off += num_threads) {
                ++buf[off];
            }
        }
    }

    // printf("verif thread counts %d %d\n", real_threkad_count, num_threads);
    printf("runtime: %lf\n", omp_get_wtime() - start_time);

    for(int i = 0; i < line_size; ++i) {
        if(i % 8 == 0 && i != 0) {
            printf("\n");
        }
        printf("%02x ", buf[i]);
    }
    printf("\n");
}