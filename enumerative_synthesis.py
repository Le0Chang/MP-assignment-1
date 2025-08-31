"""
Enumerative Synthesis Framework
This module implements the bottom-up enumerative synthesis algorithm
that works across different domain-specific languages.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, TypeVar, Generic, Generator
import numpy as np
from tqdm import tqdm

T = TypeVar('T')  # Generic type for a DSL expression

class BottomUpSynthesizer(ABC, Generic[T]):
    """Abstract base class for bottom-up enumerative synthesizers"""
    
    @abstractmethod
    def generate_terminals(self, examples: List[Any]) -> List[T]:
        """Generate terminal expressions for the DSL"""
        pass
    
    @abstractmethod
    def grow(self, program_list: List[T], examples: List[Any]) -> List[T]:
        """Grow the program list by one level using all possible operations"""
        pass
    
    @abstractmethod
    def is_correct(self, program: T, examples: List[Any]) -> bool:
        """Check if a program produces the expected output on all examples"""
        pass
    
    '''
    def synthesize(self, examples: List[Any], max_iterations: int = 5) -> T:
        """
        Main synthesis algorithm using bottom-up enumeration
        
        Args:
            examples: List of input-output examples
            max_iterations: Maximum number of growth iterations
            
        Returns:
            A program that satisfies all examples
        """
        
        if not examples:
            raise ValueError("No examples provided")
        test_inputs = self.extract_test_inputs(examples)
        
        ###################################################################################################
        #                                                                                                 #
        # Part 1 (c): Synthesizing Geometric Shapes (`synthesize`)                                        #
        #                                                                                                 #
        # TODO: Add your implementation here.                                                             #
        #                                                                                                 #
        # NOTE: Add code above the below raise statement and implement the actual synthesis logic here.   #
        #       Make sure to keep the raise statement at the end of the function, which should be reached #
        #       if no program is found within the given number of iterations.                             #
        #                                                                                                 #
        ###################################################################################################
        
        raise ValueError(f"No program found within {max_iterations} iterations")
    '''

    def synthesize(self, examples: List[Any], max_iterations: int = 5) -> T:
        """
        Main synthesis algorithm using bottom-up enumeration
    
        Args:
            examples: List of input-output examples
            max_iterations: Maximum number of growth iterations
        
        Returns:
            A program that satisfies all examples
        """
    
        if not examples:
            raise ValueError("No examples provided")
        test_inputs = self.extract_test_inputs(examples)
        cache: Dict[T, Any] = {}  # 用于存储程序的签名缓存

        # 1. 生成初始终端程序（如基础形状：矩形、圆等）
        current_programs = self.generate_terminals(examples)
    
        # 2. 消除初始程序中的等价程序
        unique_programs = list(self.eliminate_equivalents(
            current_programs, test_inputs, cache, iteration=0
        ))
    
        # 3. 检查初始程序中是否有满足条件的解
        for program in unique_programs:
            if self.is_correct(program, examples):
                return program  # 找到解，立即返回

        # 4. 迭代生长程序（最多 max_iterations 次）
        for iteration in range(1, max_iterations + 1):
            # 基于当前程序生成更复杂的程序（应用操作：并集、交集等）
            grown_programs = self.grow(unique_programs, examples)
        
            # 消除生长后的等价程序
            new_unique_programs = list(self.eliminate_equivalents(
                grown_programs, test_inputs, cache, iteration=iteration
            ))
        
            # 检查新生成的程序是否有解
            for program in new_unique_programs:
                if self.is_correct(program, examples):
                    return program  # 找到解，立即返回
        
            # 更新当前程序集（合并历史程序，避免重复生长）
            unique_programs += new_unique_programs
            # 再次消除合并后的等价程序（可选，进一步减少冗余）
            unique_programs = list(self.eliminate_equivalents(
                unique_programs, test_inputs, cache, iteration=iteration
            ))

        # 若达到最大迭代次数仍未找到解
        raise ValueError(f"No program found within {max_iterations} iterations")
    
    '''
    def eliminate_equivalents(self, program_list: List[T], test_inputs: List[Any], 
                              cache: Dict[T, Any], iteration: int) -> Generator[T, None, Dict[T, Any]]:
        """
        Eliminate equivalent programs while maintaining interpretation cache
        
        Yields:
            Unique programs one at a time
            
        Returns:
            Updated cache after processing all programs
        """
        
        ###################################################################################################
        #                                                                                                 #
        # Part 1 (b): Synthesizing Geometric Shapes (`eliminate_equivalents`)                             #
        #                                                                                                 #
        # TODO: Add your implementation here.                                                             #
        #                                                                                                 #
        # NOTE: Below is a placeholder implementation that does not eliminate observationally             #
        #       equivalent programs. You need to implement the actual elimination logic here.             #
        #       Unique programs should be yielded one at a time.                                          #
        #                                                                                                 #
        # NOTE: We use tqdm to show a progress bar. You can remove it or keep using it to show the        #
        #       progress of the synthesis process. You can also use it to show the progress of the        #
        #       other processes during the synthesis process.                                             #
        #                                                                                                 #
        ###################################################################################################
        
        for program in tqdm(program_list, desc=f"[Iteration {iteration}] Processing programs and eliminating equivalents", unit="program"):
            yield program
    '''

    def eliminate_equivalents(self, program_list: List[T], test_inputs: List[Any], 
                              cache: Dict[T, Any], iteration: int) -> Generator[T, None, Dict[T, Any]]:
        """
        Eliminate equivalent programs while maintaining interpretation cache
    
        Yields:
            Unique programs one at a time
        
        Returns:
            Updated cache after processing all programs
        """
        seen_signatures = set()  # 记录已出现的签名，用于去重

        for program in tqdm(program_list, desc=f"[Iteration {iteration}] Eliminating equivalents", unit="program"):
            # 关键：无论程序是否已在缓存中，都重新计算并更新（确保不同对象被记录）
            xs, ys = test_inputs[0]
            signature = tuple(program.interpret(xs, ys))
            cache[program] = signature  # 即使等价，不同对象也会被作为不同键存入
        
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                yield program
    
        return cache

    @abstractmethod
    def extract_test_inputs(self, examples: List[Any]) -> List[Any]:
        """Extract test inputs from examples for equivalence elimination"""
        pass

    @abstractmethod
    def compute_signature(self, program: T, test_inputs: List[Any]) -> Any:
        """Compute a signature for a program on test inputs for equivalence checking"""
        pass
