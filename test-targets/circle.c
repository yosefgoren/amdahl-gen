#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SQUARE(x) ((x)*(x))
#define N (1e5)

typedef struct point_t {
    double x;
    double y;
} point;

double distance(point* v1, point* v2) {
    return sqrtf64(SQUARE(v1->x-v2->x)+SQUARE(v1->y-v2->y));
}

double random_float() {
    double result = (double)rand() / RAND_MAX;
    return result;
}

int main(){
    srand(time(NULL));
    long in_cnt = 0;
    point v1, v2;
    for(long i = 0; i < N; ++i) {
        v1.x = random_float();
        v1.y = random_float();
        v2.x = random_float();
        v2.y = random_float();
        in_cnt += distance(&v1, &v2) > 1.0f;
    }
    printf("%lf\n", (double)in_cnt/(double)N);
}