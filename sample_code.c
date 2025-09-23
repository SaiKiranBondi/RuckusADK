#include <stdio.h>
#include <stdlib.h>

// A simple calculator structure
typedef struct {
    int result;
} Calculator;

// Calculator methods
int add(Calculator* calc, int a, int b) {
    calc->result = a + b;
    return calc->result;
}

int subtract(Calculator* calc, int a, int b) {
    calc->result = a - b;
    return calc->result;
}

// Standalone function
char* greet(const char* name) {
    static char greeting[100];
    snprintf(greeting, sizeof(greeting), "Hello, %s", name);
    return greeting;
}

// Math utility function
int multiply(int a, int b) {
    return a * b;
}