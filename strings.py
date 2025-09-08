"""
String Operations DSL Implementation
This module defines the domain-specific language for string transformations.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

class StringExpression(ABC):
    """Abstract base class for all string expressions in our DSL"""
    
    @abstractmethod
    def interpret(self, input_string: str) -> str:
        """Interpret the expression on the given input string"""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        pass
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

class StringLiteral(StringExpression):
    """A literal string constant"""
    
    def __init__(self, value: str):
        self.value = value
    
    def interpret(self, input_string: str) -> str:
        return self.value
    
    def __str__(self) -> str:
        return f'"{self.value}"'
    
    def __hash__(self) -> int:
        return hash(('literal', self.value))
    
    def __eq__(self, other) -> bool:
        return isinstance(other, StringLiteral) and self.value == other.value

class InputString(StringExpression):
    """Reference to the input string"""
    
    def interpret(self, input_string: str) -> str:
        return input_string
    
    def __str__(self) -> str:
        return "input"
    
    def __hash__(self) -> int:
        return hash('input')
    
    def __eq__(self, other) -> bool:
        return isinstance(other, InputString)

class Concatenate(StringExpression):
    """Concatenation of two string expressions"""
    
    def __init__(self, left: StringExpression, right: StringExpression):
        self.left = left
        self.right = right
    
    def interpret(self, input_string: str) -> str:
        return self.left.interpret(input_string) + self.right.interpret(input_string)
    
    def __str__(self) -> str:
        return f"Concat({self.left}, {self.right})"
    
    def __hash__(self) -> int:
        return hash(('concat', hash(self.left), hash(self.right)))
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Concatenate) and 
                self.left == other.left and self.right == other.right)

#####################################################################################################
#                                                                                                   #
# Part 2 (a): String Operations DSL                                                                 #
#                                                                                                   #
# TODO: Add your implementation here.                                                               #
#                                                                                                   #
# NOTE: Each operation should be implemented as a class that inherits from StringExpression,        #
#       similar to StringLiteral, InputString, and Concatenate. The `interpret` function encodes    #
#       semantics of the operation. `__str__`, `__hash__`, and `__eq__` are helper functions that   #
#       need to be implemented for the synthesizer to work correctly.                               #
#                                                                                                   #
#####################################################################################################