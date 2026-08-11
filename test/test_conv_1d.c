#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "conv_1d/conv_1d_float.h"
#include "conv_1d/conv_1d_double.h"

#define SIZE 100
#define KERNEL_SIZE 5
#define OUT_SIZE (SIZE-KERNEL_SIZE+1)
#define EPSILON_FLOAT 0.00001
#define EPSILON_DOUBLE 0.00000000000001

void reference_float(int size, int kernel_size, float *in, float *out, float *kernel){
int i,k;
for(i=0;i<size-kernel_size+1;++i) {
out[i]=0 ;
for(k=0;k<kernel_size;++k) {
out[i]+=(in[i+k])*(kernel[kernel_size-k-1]) ;
} 
} 
}

void reference_double(int size, int kernel_size, double *in, double *out, double *kernel){
int i,k;
for(i=0;i<size-kernel_size+1;++i) {
out[i]=0 ;
for(k=0;k<kernel_size;++k) {
out[i]+=(in[i+k])*(kernel[kernel_size-k-1]) ;
} 
} 
}

void compare_output_float(int n, float *a, float *b){
    for(int i=0;i<n;++i) {
        if(!(fabs(a[i] - b[i]) < EPSILON_FLOAT)){
            printf("Error in position %d: %f != %f\n", i, a[i], b[i]);
            exit(1);
        }
    }
}

void initialize_input_float(int size, int kernel_size, float *in, float *kernel){
    for(int i=0;i<size;++i) {
        in[i] = (float) (i*2 + 2) / size;
    }
    for(int i=0;i<kernel_size;++i) {
        kernel[i] = (float) (i*3 + 3) / kernel_size;
    }
}

void run_tests_float(){
    float *in = malloc(SIZE*sizeof(float));
    float *kernel = malloc(KERNEL_SIZE*sizeof(float));
    float *out = malloc(OUT_SIZE*sizeof(float));
    float *out_ref = malloc(OUT_SIZE*sizeof(float));

    printf("Init float\n");
    functions_float();
    printf("Running tests for float\n");
    initialize_input_float(SIZE, KERNEL_SIZE, in, kernel);
    reference_float(SIZE, KERNEL_SIZE, in, out, kernel);

    for (int i = 0; i < N_TESTS; i++) {
        printf("Running float %d \n", i+1);
        function_float[i](SIZE, KERNEL_SIZE, in, out_ref, kernel);
        compare_output_float(OUT_SIZE, out, out_ref);
    }

    free(in);
    free(kernel);
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

void initialize_input_double(int size, int kernel_size, double *in, double *kernel){
    for(int i=0;i<size;++i) {
        in[i] = (double) (i*2 + 2) / size;
    }
    for(int i=0;i<kernel_size;++i) {
        kernel[i] = (double) (i*3 + 3) / kernel_size;
    }
}

void run_tests_double(){
    double *in = malloc(SIZE*sizeof(double));
    double *kernel = malloc(KERNEL_SIZE*sizeof(double));
    double *out = malloc(OUT_SIZE*sizeof(double));
    double *out_ref = malloc(OUT_SIZE*sizeof(double));

    printf("Init double\n");
    functions_double();
    printf("Running tests for double\n");
    initialize_input_double(SIZE, KERNEL_SIZE, in, kernel);
    reference_double(SIZE, KERNEL_SIZE, in, out, kernel);

    for (int i = 0; i < N_TESTS; i++) {
        printf("Running double %d \n", i+1);
        function_double[i](SIZE, KERNEL_SIZE, in, out_ref, kernel);
        compare_output_double(OUT_SIZE, out, out_ref);
    }

    free(in);
    free(kernel);
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