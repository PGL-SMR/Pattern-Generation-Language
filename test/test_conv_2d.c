#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "conv_2d/conv_2d_float.h"
#include "conv_2d/conv_2d_double.h"

#define ROWS 10
#define COLS 14
#define KROWS 2
#define KCOLS 4
#define EPSILON_FLOAT 0.00001
#define EPSILON_DOUBLE 0.00000000000001

void reference_float(int rows, int cols, int kRows, int kCols, float **in, float **out, float **kernel){
int i,j,m,n;
int kCenterX=kCols/2;
int kCenterY=kRows/2;
for(i=0;i<rows;++i) {
for(j=0;j<cols;++j) {
out[i][j]=0 ;
for(m=0;m<kRows;++m) {
int mm=((kRows)-(1))-(m) ;
for(n=0;n<kCols;++n) {
int nn=((kCols)-(1))-(n) ;
int ii=(i)+((kCenterY)-(mm)) ;
int jj=(j)+((kCenterX)-(nn)) ;
if(ii>=0&ii<rows&jj>=0&j<cols ) {
out[i][j]+=(in[ii][jj])*(kernel[mm][nn]) ;
} 
} 
} 
} 
}
}

void reference_double(int rows, int cols, int kRows, int kCols, double **in, double **out, double **kernel){
int i,j,m,n;
int kCenterX=kCols/2;
int kCenterY=kRows/2;
for(i=0;i<rows;++i) {
for(j=0;j<cols;++j) {
out[i][j]=0 ;
for(m=0;m<kRows;++m) {
int mm=((kRows)-(1))-(m) ;
for(n=0;n<kCols;++n) {
int nn=((kCols)-(1))-(n) ;
int ii=(i)+((kCenterY)-(mm)) ;
int jj=(j)+((kCenterX)-(nn)) ;
if(ii>=0&ii<rows&jj>=0&j<cols ) {
out[i][j]+=(in[ii][jj])*(kernel[mm][nn]) ;
} 
} 
} 
} 
} 
}

void compare_output_float(int rows, int cols, float **a, float **b){
    for(int i=0;i<rows;++i) {
        for(int j=0;j<cols;++j)
        if(!(fabs(a[i][j] - b[i][j]) < EPSILON_FLOAT)){
            printf("Error in position %d: %f != %f\n", i, a[i][j], b[i][j]);
            exit(1);
        }
    }
}

void initialize_input_float(int rows, int cols, int kRows, int kCols, float **in, float **kernel){
    for(int i=0;i<rows;++i) {
        for(int j=0;j<cols;++j)
        in[i][j] = (float) ((i*2 + 2)%rows + j) / cols;
    }
    for(int i=0;i<kRows;++i) {
        for(int j=0;j<kCols;++j)
        kernel[i][j] = (float) ((i*3 + 3)%kRows + j) / kCols;
    }
}

void alloc_2d_float(float ***array, int rows, int cols){
    *array = (float **) malloc(rows*sizeof(float *));
    for (int i = 0; i < rows; i++) {
        (*array)[i] = (float *) malloc(cols*sizeof(float));
    }
}

void alloc_2d_double(double ***array, int rows, int cols){
    *array = (double **) malloc(rows*sizeof(double *));
    for (int i = 0; i < rows; i++) {
        (*array)[i] = (double *) malloc(cols*sizeof(double));
    }
}

void free_2d_float(float **array, int rows){
    for (int i = 0; i < rows; i++) {
        free(array[i]);
    }
    free(array);
}

void free_2d_double(double **array, int rows){
    for (int i = 0; i < rows; i++) {
        free(array[i]);
    }
    free(array);
}

void run_tests_float(){
    float **in, **kernel, **out, **out_ref;

    alloc_2d_float(&in, ROWS, COLS);
    alloc_2d_float(&kernel, KROWS, KCOLS);
    alloc_2d_float(&out, ROWS, COLS);
    alloc_2d_float(&out_ref, ROWS, COLS);

    printf("Init float\n");
    functions_float();
    printf("Running tests for float\n");
    initialize_input_float(ROWS, COLS, KROWS, KCOLS, in, kernel);
    reference_float(ROWS, COLS, KROWS, KCOLS, in, out_ref, kernel);

    for (int i = 0; i < N_TESTS; i++) {
        printf("Running float %d \n", i+1);
        function_float[i](ROWS, COLS, KROWS, KCOLS, in, out, kernel);
        compare_output_float(ROWS, COLS, out, out_ref);
    }

    free_2d_float(in, ROWS);
    free_2d_float(kernel, KROWS);
    free_2d_float(out, ROWS);
    free_2d_float(out_ref, ROWS);
    free(function_float);
}

void compare_output_double(int rows, int cols, double **a, double **b){
    for(int i=0;i<rows;++i) {
        for(int j=0;j<cols;++j)
        if(!(fabs(a[i][j] - b[i][j]) < EPSILON_DOUBLE)){
            printf("Error in position %d: %f != %f\n", i, a[i][j], b[i][j]);
            exit(1);
        }
    }
}

void initialize_input_double(int rows, int cols, int kRows, int kCols, double **in, double **kernel){
    for(int i=0;i<rows;++i) {
        for(int j=0;j<cols;++j)
        in[i][j] = (double) ((i*2 + 2)%rows + j) / cols;
    }
    for(int i=0;i<kRows;++i) {
        for(int j=0;j<kCols;++j)
        kernel[i][j] = (double) ((i*3 + 3)%kRows + j) / kCols;
    }
}

void run_tests_double(){
    double **in, **kernel, **out, **out_ref;


    alloc_2d_double(&in, ROWS, COLS);
    alloc_2d_double(&kernel, KROWS, KCOLS);
    alloc_2d_double(&out, ROWS, COLS);
    alloc_2d_double(&out_ref, ROWS, COLS);

    printf("Init double\n");
    functions_double();
    printf("Running tests for double\n");
    initialize_input_double(ROWS, COLS, KROWS, KCOLS, in, kernel);
    reference_double(ROWS, COLS, KROWS, KCOLS, in, out_ref, kernel);

    for (int i = 0; i < N_TESTS; i++) {
        printf("Running double %d \n", i+1);
        function_double[i](ROWS, COLS, KROWS, KCOLS, in, out, kernel);
        compare_output_double(ROWS, COLS, out, out_ref);
    }

    free_2d_double(in, ROWS);
    free_2d_double(kernel, KROWS);
    free_2d_double(out, ROWS);
    free_2d_double(out_ref, ROWS);
    free(function_double);
}

int main(){
    run_tests_float();
    run_tests_double();
    printf("Success!\n");
    return 0;
}