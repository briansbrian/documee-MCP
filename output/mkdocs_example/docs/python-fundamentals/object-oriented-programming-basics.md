# Object-Oriented Programming Basics

**Difficulty**: intermediate | **Duration**: 45 minutes

## Learning Objectives

- Understand class structure
- Create class instances
- Define methods

## Prerequisites

- lesson-1

## Introduction

Classes are blueprints for creating objects with attributes and methods.

## Explanation

Object-oriented programming allows you to organize code into reusable, modular structures.

## Code Example

```python
class Person:
    """Represents a person with a name and age."""
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def introduce(self):
        return f"Hi, I'm {self.name} and I'm {self.age} years old."

# Create an instance
person = Person("Alice", 30)
print(person.introduce())
```


## Walkthrough

This Person class demonstrates how to define attributes in __init__ and create methods.

## Summary

You learned the basics of classes and object-oriented programming.

## Further Reading

- Python Classes Tutorial
- OOP Principles


## Tags

`python` `OOP` `classes`