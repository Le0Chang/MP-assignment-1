"""
LLM-based Program Synthesis
This module uses Gemini 2.5 Pro to generate string operation programs
from input-output examples through carefully crafted prompts.
"""

import json
import os
from typing import List, Tuple, Optional
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from strings import *

class LLMPromptAndResponseLogger:
    """
    Logger for LLM prompt and response
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.prompt = ""
        self.response = ""
        self.program = None
        self.examples = []
        self.error = None

    def log_prompt(self, prompt: str, examples: List[Tuple[str, str]]):
        self.prompt = str(prompt)
        self.examples = str(examples)

    def log_response(self, response: GenerateContentResponse):
        self.response = str(response)

    def log_program(self, program: StringExpression):
        self.program = str(program)

    def log_error(self, error: Exception):
        self.error = str(error)

    def save(self):
        # dump into jsonl file as a single line
        with open(self.file_path, 'a') as f:
            f.write(json.dumps({'prompt': self.prompt, 'response': self.response, 'examples': self.examples, 'program': self.program, 'error': self.error}) + '\n')
            f.flush()

class LLMStringSynthesizer:
    """LLM-based synthesizer using Gemini 2.5 Pro"""
    
    def __init__(self, api_key: Optional[str] = None, logger: Optional[LLMPromptAndResponseLogger] = None):
        """
        Initialize the LLM synthesizer
        
        Args:
            api_key: Gemini API key. If None, will try to get from environment
        """
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.logger = logger

    def synthesize(self, examples: List[Tuple[str, str]], max_iterations: int = 5) -> StringExpression:
        """
        Synthesize a string expression from input-output examples using LLM
        
        Args:
            examples: List of (input, output) string pairs
            max_iterations: Maximum number of growth iterations (unused in LLM approach)
            
        Returns:
            StringExpression that satisfies the examples
        """
        if not examples:
            raise ValueError("No examples provided")
        
        # Create the prompt template with DSL description and examples
        prompt = self.generate_prompt(examples)

        if self.logger:
            self.logger.log_prompt(prompt, examples)
        
        try:
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            if self.logger:
                self.logger.log_response(response)
            program_text = response.text.strip()
            
            # Extract and evaluate the program
            program = self.extract_program(program_text)
            if self.logger:
                self.logger.log_program(program)

            if self.logger:
                self.logger.save()

            # Validate the program against examples
            if self.validate_program(program, examples):
                return program
            else:
                raise ValueError(f"Generated program does not satisfy all examples: {program}")
                
        except Exception as e:
            if self.logger:
                self.logger.log_error(e)
                self.logger.save()

            raise ValueError(f"Failed to synthesize program: {str(e)}")
    
    '''
    def generate_prompt(self, examples: List[Tuple[str, str]]) -> str:
        """
        Create a comprehensive prompt template for the LLM including DSL description and examples
        """
        
        #####################################################################################################
        #                                                                                                   #
        # Part 3 (a): Creating a Prompt Template (`generate_prompt`)                                        #
        #                                                                                                   #
        # TODO: Add your implementation here.                                                               #
        #                                                                                                   #
        # NOTE: Below is a placeholder implementation that does not generate a prompt template. You need to #
        #       implement the actual prompt template generation logic here.                                 #
        #                                                                                                   #
        #####################################################################################################

        return "Please write a program"
    '''

    def generate_prompt(self, examples: List[Tuple[str, str]]) -> str:
        dsl_description = """
    You are to synthesize a string processing program using the following DSL:
    - InputString(): refers to the input string
    - StringLiteral(value): creates a literal string
    - Concatenate(a, b): concatenates two strings
    - Substring(a, start, end): substring of a from start to end (Python-like slicing)
    - ToUpper(a): converts a to upper case
    - ToLower(a): converts a to lower case
    - Replace(a, old, new): replaces all occurrences of old in a with new
    - Strip(a): trims whitespace at both ends of a
    - Repeat(a, n): repeats a for n times
    - SplitThenTake(a, delim, idx): splits a by delim and takes piece idx
    - Capitalize(a): capitalizes a (first letter upper, rest lower)
    (You may use nested calls. Only output an expression in this DSL.)

    Examples for the specific task:
    """
        example_lines = []
        for inp, out in examples:
            example_lines.append(f'Input: "{inp}"   Output: "{out}"')
        prompt = dsl_description + "\n".join(example_lines)
        prompt += "\nYour output:"
        return prompt

    '''
    def extract_program(self, response_text: str) -> StringExpression:
        """
        Extract the program from LLM response and evaluate it to get StringExpression object
        """

        #####################################################################################################
        #                                                                                                   #
        # Part 3 (b): Extract the StringExpression from the LLM response (`extract_program`)                #
        #                                                                                                   #
        # TODO: Add your implementation here.                                                               # 
        #                                                                                                   #
        # NOTE: Below is a placeholder implementation that does not extract the StringExpression from the   #
        #       LLM response. You need to implement the actual extraction logic here.                       #
        #                                                                                                   #
        #####################################################################################################

        return StringLiteral("Dummy program")
    '''

    def extract_program(self, response: str) -> StringExpression:
        import re
        from strings import StringExpression, StringLiteral, InputString, Concatenate, Substring, ToUpper, ToLower, Replace, Strip, Repeat, SplitThenTake, Capitalize
        # 提取第一个合法DSL表达式（可改进为更严格正则）
        code_line = None
        # 保守找第一行有"InputString"等关键字的行
        for line in response.strip().splitlines():
            if any(k in line for k in ["InputString", "Concatenate", "Substring", "ToUpper",
                                    "ToLower", "Replace", "Strip", "Repeat", "SplitThenTake", "Capitalize"]):
                code_line = line.strip()
                break
        if code_line is None:
            raise ValueError("No recognizable DSL code found in LLM response")
        # eval时限定全局，只允许你的DSL类
        context = {
            'StringLiteral': StringLiteral, 'InputString': InputString, 'Concatenate': Concatenate,
            'Substring': Substring, 'ToUpper': ToUpper, 'ToLower': ToLower, 'Replace': Replace,
            'Strip': Strip, 'Repeat': Repeat, 'SplitThenTake': SplitThenTake, 'Capitalize': Capitalize
        }
        try:
            program = eval(code_line, context)
        except Exception as e:
            raise ValueError(f"Failed to parse LLM code: {code_line}") from e
        return program
    
    def validate_program(self, program: StringExpression, examples: List[Tuple[str, str]]) -> bool:
        """
        Validate that the generated program works correctly on all examples
        """
        try:
            for input_str, expected_output in examples:
                actual_output = program.interpret(input_str)
                if actual_output != expected_output:
                    return False
            return True
        except Exception:
            return False
