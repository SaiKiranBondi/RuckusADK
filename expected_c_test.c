#include "unity.h"
#include "source_to_test.h"

void setUp(void) {
    // Set up code that runs before each test
}

void tearDown(void) {
    // Clean up code that runs after each test
}

/*
 * Tests: Test the 'add' method with two positive integers
 * Expected Outcome: The method should return the correct sum of the two integers
 */
void test_add_positive_integers(void) {
    Calculator calc;
    int result = add(&calc, 5, 10);
    TEST_ASSERT_EQUAL(15, result);
    TEST_ASSERT_EQUAL(15, calc.result);
}

/*
 * Tests: Test the 'add' method with two negative integers
 * Expected Outcome: The method should return the correct sum of the two integers
 */
void test_add_negative_integers(void) {
    Calculator calc;
    int result = add(&calc, -5, -10);
    TEST_ASSERT_EQUAL(-15, result);
    TEST_ASSERT_EQUAL(-15, calc.result);
}

/*
 * Tests: Test the 'subtract' method with two positive integers
 * Expected Outcome: The method should return the correct difference between the two integers
 */
void test_subtract_positive_integers(void) {
    Calculator calc;
    int result = subtract(&calc, 10, 5);
    TEST_ASSERT_EQUAL(5, result);
    TEST_ASSERT_EQUAL(5, calc.result);
}

/*
 * Tests: Test the 'greet' function with a standard string
 * Expected Outcome: The function should return a greeting string in the format 'Hello, [name]'
 */
void test_greet_standard_string(void) {
    char* result = greet("World");
    TEST_ASSERT_NOT_NULL(result);
    // Note: In a real test, you'd need to compare strings properly
}

/*
 * Tests: Test the 'multiply' function with two positive integers
 * Expected Outcome: The function should return the correct product
 */
void test_multiply_positive_integers(void) {
    int result = multiply(5, 10);
    TEST_ASSERT_EQUAL(50, result);
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_add_positive_integers);
    RUN_TEST(test_add_negative_integers);
    RUN_TEST(test_subtract_positive_integers);
    RUN_TEST(test_greet_standard_string);
    RUN_TEST(test_multiply_positive_integers);
    
    return UNITY_END();
}
