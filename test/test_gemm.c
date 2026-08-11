#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "gemm/gemm_float.h"
#include "gemm/gemm_double.h"

#define M 100
#define N 50
#define K 200
#define EPSILON_FLOAT 0.00001
#define EPSILON_DOUBLE 0.00000000000001

void reference_float(int m, int n, int k, int lda, int ldb, int ldc, float alpha, float *A, float *B, float beta, float *C){
int mm, nn, i;
for(mm=0;mm<m;++mm) {
for(nn=0;nn<n;++nn) {
float c=0 ;
for(i=0;i<k;++i) {
float a=A[mm+i*lda] ;
float b=B[nn+i*ldb] ;
c+=a*b ;
} 
C[mm+nn*ldc]=C[mm+nn*ldc]*beta+alpha*c ;
} 
}
}

void reference_double(int m, int n, int k, int lda, int ldb, int ldc, double alpha, double *A, double *B, double beta, double *C){
int mm, nn, i;
for(mm=0;mm<m;++mm) {
for(nn=0;nn<n;++nn) {
double c=0 ;
for(i=0;i<k;++i) {
double a=A[mm+i*lda];
double b=B[nn+i*ldb];
c+=a*b ;
} 
C[mm+nn*ldc]=C[mm+nn*ldc]*beta+alpha*c ;
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

void initialize_input_float(int m, int n, int k, float *a, float *b, float *c){
    for(int i=0;i<m*k;++i) {
        a[i] = (float) ((i*2 + 2)%k) / k;
    }
    for(int i=0;i<n*k;++i) {
        b[i] = (float) ((i*3 + 3)%n) / n;
    }
    for(int i=0;i<m*n;++i) {
        c[i] = (float) ((i*4 + 4)%m) / m;
    }
}

void run_tests_float(){
    float *a = malloc(M*K*sizeof(float));
    float *b = malloc(K*N*sizeof(float));
    float *c = malloc(M*N*sizeof(float));
    float *c_ref = malloc(M*N*sizeof(float));

    printf("Init float\n");
    functions_float();
    printf("Running tests for float\n");
    initialize_input_float(M, N, K, a, b, c);
    reference_float(M, N, K, M, N, M, 1.5, a, b, 1.2, c);

    for (int i = 0; i < N_TESTS; i++) {
        printf("Running float %d \n", i+1);
        initialize_input_float(M, N, K, a, b, c_ref);
        function_float[i](M, N, K, M, N, M, 1.5, a, b, 1.2, c_ref);
        compare_output_float(M*N, c, c_ref);
    }

    free(a);
    free(b);
    free(c);
    free(c_ref);
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

void initialize_input_double(int m, int n, int k, double *a, double *b, double *c){
    for(int i=0;i<m*k;++i) {
        a[i] = (double) ((i*2 + 2)%k) / k;
    }
    for(int i=0;i<n*k;++i) {
        b[i] = (double) ((i*3 + 3)%n) / n;
    }
    for(int i=0;i<m*n;++i) {
        c[i] = (double) ((i*4 + 4)%m) / m;
    }
}

void run_tests_double(){
    double *a = malloc(M*K*sizeof(double));
    double *b = malloc(K*N*sizeof(double));
    double *c = malloc(M*N*sizeof(double));
    double *c_ref = malloc(M*N*sizeof(double));

    printf("Init double\n");
    functions_double();
    printf("Running tests for double\n");
    initialize_input_double(M, N, K, a, b, c);
    reference_double(M, N, K, M, N, M, 1.5, a, b, 1.2, c);

    for (int i = 0; i < N_TESTS; i++) {
        printf("Running double %d \n", i+1);
        initialize_input_double(M, N, K, a, b, c_ref);
        function_double[i](M, N, K, M, N, M, 1.5, a, b, 1.2, c_ref);
        compare_output_double(M*N, c, c_ref);
    }

    free(a);
    free(b);
    free(c);
    free(c_ref);
    free(function_double);
}

int main(){
    run_tests_float();
    run_tests_double();
    printf("Success!\n");
    return 0;
}