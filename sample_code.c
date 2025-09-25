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

// Main function for demonstration
int main() {
    printf("Simple C Functions Demo\n");
    printf("======================\n");
    
    printf("add(5, 3) = %d\n", add(5, 3));
    printf("get_length(\"hello\") = %d\n", get_length("hello"));
    printf("is_positive(5) = %d\n", is_positive(5));
    printf("is_positive(-3) = %d\n", is_positive(-3));
    
    return 0;
}
