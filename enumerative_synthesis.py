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

    def synthesize(self, examples: List[Any], max_iterations: int = 5, accumulate_programs: bool = False) -> T:
        """
        增强版合成算法：支持累积程序集（适配 Part2 组合需求），默认关闭（适配 Part1）
        
        Args:
            accumulate_programs: 是否累积所有历史程序（Part2 设为 True，Part1 保持 False）
        """
        if not examples:
            raise ValueError("No examples provided")
        test_inputs = self.extract_test_inputs(examples)
        cache: Dict[T, Any] = {}

        # 1. 生成初始终端程序
        current_programs = self.generate_terminals(examples)
        # 去重并检查初始程序
        unique_programs = list(self.eliminate_equivalents(current_programs, test_inputs, cache, iteration=0))
        for program in unique_programs:
            if self.is_correct(program, examples):
                return program

        # 2. 迭代生长：根据参数选择“累积程序”或“增量程序”
        all_programs = unique_programs.copy()  # 累积所有有效程序（仅当 accumulate_programs=True 时使用）
        for iteration in range(1, max_iterations + 1):
            # 生长基础：Part2 用累积的所有程序，Part1 用上次的新程序（兼容原有逻辑）
            grow_base = all_programs if accumulate_programs else unique_programs
            grown_programs = self.grow(grow_base, examples)
            
            # 去重新程序
            new_unique_programs = list(self.eliminate_equivalents(grown_programs, test_inputs, cache, iteration=iteration))
            if not new_unique_programs:
                break  # 无新程序，提前终止
            
            # 检查新程序是否正确
            for program in new_unique_programs:
                if self.is_correct(program, examples):
                    return program
            
            # 更新程序集：累积模式保留所有程序，非累积模式仅保留新程序（兼容 Part1）
            if accumulate_programs:
                all_programs += new_unique_programs
                # 二次去重（避免累积重复）
                all_programs = list(self.eliminate_equivalents(all_programs, test_inputs, cache, iteration=iteration))
            else:
                unique_programs = new_unique_programs

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
        增强版等价性消除：过滤空签名（无效程序），兼容 Part1
        """
        seen_signatures = set()  # 记录已出现的签名，用于去重

        for program in tqdm(program_list, desc=f"[Iteration {iteration}] Eliminating equivalents", unit="program"):
            try:
                # 调用 compute_signature 生成签名（Part1/Part2 各自实现，不影响）
                signature = self.compute_signature(program, test_inputs)
                cache[program] = signature  # 缓存签名
                
                # 过滤：跳过空签名（解释报错的无效程序）和已存在的签名
                if signature is not None and signature not in seen_signatures:
                    seen_signatures.add(signature)
                    yield program
            except Exception as e:
                # 捕获程序解释异常，跳过无效程序（Part2 组合程序可能报错，Part1 不受影响）
                cache[program] = None
                continue

        return cache

    @abstractmethod
    def extract_test_inputs(self, examples: List[Any]) -> List[Any]:
        """Extract test inputs from examples for equivalence elimination"""
        pass

    @abstractmethod
    def compute_signature(self, program: T, test_inputs: List[Any]) -> Any:
        """Compute a signature for a program on test inputs for equivalence checking"""
        pass
