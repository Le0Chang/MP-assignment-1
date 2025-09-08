from typing import List, Tuple, Any
from tqdm import tqdm

from enumerative_synthesis import BottomUpSynthesizer
from strings import StringExpression, StringLiteral, InputString, Concatenate
# TODO: import other used string operations here

class StringSynthesizer(BottomUpSynthesizer[StringExpression]):
    """Bottom-up enumerative synthesizer for string expressions"""
    
    def __init__(self):
        # Common literals needed for the synthesis
        self.common_literals = [
            "", " ", ".", ",", "-", "/", "_", ":", ";", "!", "?", "*", "#", "@", "$", ".", "0", "\\"
        ]
        
        # Common indices for substring operations
        self.common_indices = [0, 1, 2, 3, 4, 5, -1, -2]
    
        # Repeat counts used in test cases
        self.common_repeat_counts = [1, 2, 3]
        
        # Maximum number of concatenate operations allowed
        self.max_concatenations = 3
    
    def generate_terminals(self, examples: List[Tuple[str, str]]) -> List[StringExpression]:
        """Generate terminal expressions based on input examples"""
        terminals = []
        
        # Always include input reference
        terminals.append(InputString())
        
        # Add common string literals
        for literal in tqdm(self.common_literals, desc="Common literals", unit="literal"):
            appeared = False
            for (input, output) in examples:
                if literal in output:
                    appeared = True
                    break
            if appeared:
                terminals.append(StringLiteral(literal))
        
        return terminals
    
    def grow(self, program_list: List[StringExpression], examples: List[Any]) -> List[StringExpression]:
        """
        Grow the program list by one level using all possible operations.
        Students should implement this method to include all required DSL operations.
        """
        
        ###################################################################################################
        #                                                                                                 #
        # Part 2 (b): Synthesizing String Expressions (`grow`)                                            #
        #                                                                                                 #
        # TODO: Add your implementation here.                                                             #
        #                                                                                                 #
        # NOTE: Below is a placeholder implementation that does not grow the program list. You need to    #
        #       implement the actual growth logic here.                                                   #
        #                                                                                                 #
        ###################################################################################################

        new_programs = []
        
        return new_programs
    
    def is_correct(self, program: StringExpression, examples: List[Tuple[str, str]]) -> bool:
        """Check if a program produces the expected output on all examples"""
        try:
            for input_str, expected_output in examples:
                result = program.interpret(input_str)
                if result != expected_output:
                    return False
            return True
        except Exception:
            return False
    
    def extract_test_inputs(self, examples: List[Tuple[str, str]]) -> List[str]:
        """Extract test inputs from examples for equivalence elimination"""
        return [ex[0] for ex in examples]

    def compute_signature(self, program: StringExpression, test_inputs: List[str]) -> Any:
        """Compute a signature for a string expression on test inputs for equivalence checking"""
        try:
            return tuple(program.interpret(inp) for inp in test_inputs)
        except Exception:
            return None # Indicate failure to interpret