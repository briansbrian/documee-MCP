# Introduction to Functions

**Difficulty**: beginner | **Duration**: 30 minutes

## Learning Objectives

- Understand function syntax
- Define functions with parameters
- Return values from functions


## Introduction

Functions are reusable blocks of code that perform specific tasks.

## Explanation

In Python, functions are defined using the `def` keyword followed by the function name and parameters.

## Code Example

```python
def greet(name):
    """Greet someone by name."""
    return f"Hello, {name}!"

# Usage
message = greet("World")
print(message)
```

### Code Annotations

**Line 1**: Define a function that takes a name parameter
**Line 2**: Use an f-string to format the greeting
**Line 5**: Call the function with an argument

## Walkthrough

This example shows a simple greeting function that takes a name and returns a formatted message.

## Summary

You learned how to define and call functions in Python.

## Further Reading

- Python Functions Documentation
- Best Practices for Function Design

## Exercises

### Create a Calculator Function

Write a function that performs basic arithmetic operations.

**Difficulty**: beginner | **Estimated Time**: 15 minutes

#### Instructions

1. Define a function called 'calculate' that takes three parameters: num1, num2, and operation
2. Support operations: 'add', 'subtract', 'multiply', 'divide'
3. Return the result of the operation
4. Handle division by zero

#### Starter Code

```python
def calculate(num1, num2, operation):
    # TODO: Implement the calculator logic
    pass
```

#### Hints

<details>
<summary>Hint 1</summary>

Use if-elif statements to check the operation type

</details>
<details>
<summary>Hint 2</summary>

Remember to check for division by zero before dividing

</details>

#### Test Cases

**Test 1**: Test addition
- Input: `calculate(5, 3, 'add')`
- Expected: `8`
**Test 2**: Test division
- Input: `calculate(10, 2, 'divide')`
- Expected: `5.0`
**Test 3**: Test division by zero
- Input: `calculate(5, 0, 'divide')`
- Expected: `Error: Division by zero`

---


## Tags

`python` `functions` `basics`