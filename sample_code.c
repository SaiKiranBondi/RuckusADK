#include <stdio.h>

// Simple math function
int add(int a, int b) {
    return a + b;
}

// Simple string function
int get_length(const char* str) {
    if (str == NULL) return -1;
    int len = 0;
    while (str[len] != '\0') {
        len++;
    }
    return len;
}

// Simple validation function
int is_positive(int number) {
    return number > 0;
}