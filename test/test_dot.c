#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "dot/dot_float.h"
#include "dot/dot_double.h"

#define N_OUT 1
#define N_IN 100
#define EPSILON_FLOAT 0.00001
#define EPSILON_DOUBLE 0.00000000000001

float reference_float(int n, float *x, float *y, float out){
out=0;
for(int i=0;i<n;++i) {
out+=(x[i])*(y[i]) ;
}
return out;
}

double reference_double(int n, double *x, double *y, double out){
out=0;
for(int i=0;i<n;++i) {
out+=(x[i])*(y[i]) ;
}
return out;
}

void compare_output_float(int n, float *a, float *b){
    for(int i=0;i<n;++i) {
        if(!(fabs(a[i] - b[i]) < EPSILON_FLOAT)){
            printf("Error in position %d: %f != %f\n", i, a[i], b[i]);
            exit(1);
        }
    }
}

void initialize_input_float(int n, float *x, float *y){
    for(int i=0;i<n;++i) {
        x[i] = (i*2 + 2) / n;
        y[i] = (i*3 + 3) / n;
    }
}

void run_tests_float(){
    float *x = malloc(N_IN*sizeof(float));
    float *y = malloc(N_IN*sizeof(float));
    float *out = malloc(N_OUT*sizeof(float));
    float *out_ref = malloc(N_OUT*sizeof(float));

    functions_float();
    initialize_input_float(N_IN, x, y);
    *out_ref = reference_float(N_IN, x, y, 0);

    for (int i = 0; i < N_TESTS; i++) {
        *out = function_float[i](N_IN, x, y, 0);
        compare_output_float(N_OUT, out, out_ref);
    }

    free(x);
    free(y);
    free(out);
    free(out_ref);
    free(function_float);
}

void compare_output_double(int n, double *a, double *b){
    for(int i=0;i<n;++i) {
        if(!(fabs(a[i] - b[i]) < EPSILON_DOUBLE)){
            printf("Error in position %d: %f != %f\n", i, a[i], b[i]);
            exit(1);
        }
    }
}

void initialize_input_double(int n, double *x, double *y){
    for(int i=0;i<n;++i) {
        x[i] = (i*2 + 2) / n;
        y[i] = (i*3 + 3) / n;
    }
}

void run_tests_double(){
    double *x = malloc(N_IN*sizeof(double));
    double *y = malloc(N_IN*sizeof(double));
    double *out = malloc(N_OUT*sizeof(double));
    double *out_ref = malloc(N_OUT*sizeof(double));

    functions_double();
    initialize_input_double(N_IN, x, y);
    *out_ref = reference_double(N_IN, x, y, 0);

    for (int i = 0; i < N_TESTS; i++) {
        *out = function_double[i](N_IN, x, y, 0);
        compare_output_double(N_OUT, out, out_ref);
    }

    free(x);
    free(y);
    free(out);
    free(out_ref);
    free(function_double);
}

int main(){
    run_tests_float();
    run_tests_double();
    printf("Success!\n");
    return 0;
}