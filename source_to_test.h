#ifndef SOURCE_TO_TEST_H
#define SOURCE_TO_TEST_H

#include <stdio.h>
#include <stdlib.h>

// Calculator structure
typedef struct {
    int result;
} Calculator;

// Function declarations
int add(Calculator* calc, int a, int b);
int subtract(Calculator* calc, int a, int b);
char* greet(const char* name);
int multiply(int a, int b);

#endif
