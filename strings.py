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

class Substring(StringExpression):
    """截取子串（遵循Python切片规则：start_idx起始，end_idx结束，左闭右开）"""
    def __init__(self, expr: StringExpression, start_idx: int, end_idx: int):
        self.expr = expr  # 源字符串表达式
        self.start_idx = start_idx  # 起始索引（支持负数）
        self.end_idx = end_idx      # 结束索引（支持负数）

    def interpret(self, input_string: str) -> str:
        source = self.expr.interpret(input_string)
        try:
            return source[self.start_idx:self.end_idx]
        except IndexError:  # 索引越界返回空串
            return ""

    def __str__(self) -> str:
        return f"Substring({self.expr}, {self.start_idx}, {self.end_idx})"

    def __hash__(self) -> int:
        return hash(('substring', hash(self.expr), self.start_idx, self.end_idx))

    def __eq__(self, other) -> bool:
        return (isinstance(other, Substring) and
                self.expr == other.expr and
                self.start_idx == other.start_idx and
                self.end_idx == other.end_idx)


class ToUpper(StringExpression):
    """将字符串转换为全大写"""
    def __init__(self, expr: StringExpression):
        self.expr = expr

    def interpret(self, input_string: str) -> str:
        return self.expr.interpret(input_string).upper()

    def __str__(self) -> str:
        return f"ToUpper({self.expr})"

    def __hash__(self) -> int:
        return hash(('to_upper', hash(self.expr)))

    def __eq__(self, other) -> bool:
        return isinstance(other, ToUpper) and self.expr == other.expr


class ToLower(StringExpression):
    """将字符串转换为全小写"""
    def __init__(self, expr: StringExpression):
        self.expr = expr

    def interpret(self, input_string: str) -> str:
        return self.expr.interpret(input_string).lower()

    def __str__(self) -> str:
        return f"ToLower({self.expr})"

    def __hash__(self) -> int:
        return hash(('to_lower', hash(self.expr)))

    def __eq__(self, other) -> bool:
        return isinstance(other, ToLower) and self.expr == other.expr


class Replace(StringExpression):
    """替换字符串中的子串（old_sub → new_sub）"""
    def __init__(self, expr: StringExpression, old_sub: StringExpression, new_sub: StringExpression):
        self.expr = expr      # 源字符串
        self.old_sub = old_sub  # 要替换的旧子串
        self.new_sub = new_sub  # 替换后的新子串

    def interpret(self, input_string: str) -> str:
        source = self.expr.interpret(input_string)
        old = self.old_sub.interpret(input_string)
        new = self.new_sub.interpret(input_string)
        return source.replace(old, new)

    def __str__(self) -> str:
        return f"Replace({self.expr}, {self.old_sub}, {self.new_sub})"

    def __hash__(self) -> int:
        return hash(('replace', hash(self.expr), hash(self.old_sub), hash(self.new_sub)))

    def __eq__(self, other) -> bool:
        return (isinstance(other, Replace) and
                self.expr == other.expr and
                self.old_sub == other.old_sub and
                self.new_sub == other.new_sub)


class Strip(StringExpression):
    """去除字符串首尾空白（空格、制表符\t、换行符\n）"""
    def __init__(self, expr: StringExpression):
        self.expr = expr

    def interpret(self, input_string: str) -> str:
        return self.expr.interpret(input_string).strip()

    def __str__(self) -> str:
        return f"Strip({self.expr})"

    def __hash__(self) -> int:
        return hash(('strip', hash(self.expr)))

    def __eq__(self, other) -> bool:
        return isinstance(other, Strip) and self.expr == other.expr


class Repeat(StringExpression):
    """将字符串重复n次（n≥1）"""
    def __init__(self, expr: StringExpression, count: int):
        if count < 1:
            raise ValueError("Repeat count must be ≥ 1")
        self.expr = expr
        self.count = count

    def interpret(self, input_string: str) -> str:
        return self.expr.interpret(input_string) * self.count

    def __str__(self) -> str:
        return f"Repeat({self.expr}, {self.count})"

    def __hash__(self) -> int:
        return hash(('repeat', hash(self.expr), self.count))

    def __eq__(self, other) -> bool:
        return (isinstance(other, Repeat) and
                self.expr == other.expr and
                self.count == other.count)


class SplitThenTake(StringExpression):
    """按分隔符分割字符串，取指定索引的片段（解决“取姓/名/域名”等用例）"""
    def __init__(self, expr: StringExpression, delimiter: StringExpression, index: int):
        self.expr = expr        # 源字符串
        self.delimiter = delimiter  # 分隔符（如空格、@、.）
        self.index = index      # 要取的片段索引（支持负数，如-1取最后一个）

    def interpret(self, input_string: str) -> str:
        source = self.expr.interpret(input_string)
        delim = self.delimiter.interpret(input_string)
        parts = source.split(delim)
        try:
            return parts[self.index]
        except IndexError:  # 索引无效返回空串
            return ""

    def __str__(self) -> str:
        return f"SplitThenTake({self.expr}, {self.delimiter}, {self.index})"

    def __hash__(self) -> int:
        return hash(('split_take', hash(self.expr), hash(self.delimiter), self.index))

    def __eq__(self, other) -> bool:
        return (isinstance(other, SplitThenTake) and
                self.expr == other.expr and
                self.delimiter == other.delimiter and
                self.index == other.index)

class Capitalize(StringExpression):
    """将字符串首字母大写，其余字符保持原样（适配 generate_password_hint 用例）"""
    def __init__(self, expr: StringExpression):
        self.expr = expr

    def interpret(self, input_string: str) -> str:
        # 调用 Python 原生 capitalize() 方法：首字母大写，其余小写（如 "password"→"Password"）
        return self.expr.interpret(input_string).capitalize()

    def __str__(self) -> str:
        return f"Capitalize({self.expr})"

    def __hash__(self) -> int:
        return hash(('capitalize', hash(self.expr)))

    def __eq__(self, other) -> bool:
        return isinstance(other, Capitalize) and self.expr == other.expr
