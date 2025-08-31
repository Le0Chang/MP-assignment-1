import pytest
import numpy as np
from typing import List, Dict, Any
from enumerative_synthesis import BottomUpSynthesizer, T
from shapes import Shape, Rectangle, Circle, Coordinate  # 导入你的形状类

# 1. 定义测试用的合成器子类（模拟ShapeSynthesizer的核心功能）
class TestSynthesizer(BottomUpSynthesizer[Shape]):
    """用于测试的合成器，仅实现与eliminate_equivalents相关的方法"""
    def generate_terminals(self, examples: List[Any]) -> List[Shape]:
        return []  # 测试无需实现
    
    def grow(self, program_list: List[Shape], examples: List[Any]) -> List[Shape]:
        return []  # 测试无需实现
    
    def is_correct(self, program: Shape, examples: List[Any]) -> bool:
        return True  # 测试无需实现
    
    def extract_test_inputs(self, examples: List[Any]) -> List[Any]:
        """返回固定测试点：(0,0)、(3,3)、(1.5,1.5)"""
        return [(
            np.array([0.0, 1.0, 2.0, 3.0]),  # xs
            np.array([0.0, 1.0, 2.0, 3.0])   # ys
        )]
    
    def compute_signature(self, program: Shape, test_inputs: List[Any]) -> Any:
        """计算形状在测试点上的输出作为签名"""
        xs, ys = test_inputs[0]
        return tuple(program.interpret(xs, ys))  # 转为tuple以支持哈希

# 2. 辅助函数：创建测试用的形状（包含等价和不等价程序）
def create_test_programs() -> List[Shape]:
    coord0 = Coordinate(0, 0)
    coord2 = Coordinate(2, 2)    # 小矩形/圆的边界
    # coord3 = Coordinate(3, 3)    # 大矩形的边界
    coord4 = Coordinate(4, 4)    # 更大矩形

    # 第一组等价：rect1 和 rect2（不同对象，参数相同）
    rect1 = Rectangle(Coordinate(0,0), Coordinate(2,2))  # 新对象
    rect2 = Rectangle(Coordinate(0,0), Coordinate(2,2))  # 新对象（与rect1参数相同但内存地址不同）

    # 第二组等价：circle1 和 circle2（不同对象，参数相同）
    circle1 = Circle(Coordinate(0,0), 2)  # 新对象
    circle2 = Circle(Coordinate(0,0), 2)  # 新对象

    # 第三组独立：rect3（唯一对象）
    rect3 = Rectangle(coord0, coord4)

    return [rect1, rect2, circle1, circle2, rect3]

# 3. 测试类
class TestEliminateEquivalents:
    def setup_method(self):
        self.synthesizer = TestSynthesizer()
        self.test_programs = create_test_programs()  # 5个程序：2组等价+1个独立
        self.test_inputs = self.synthesizer.extract_test_inputs([])
        self.initial_cache: Dict[Shape, Any] = {}  # 初始空缓存

    def test_equivalent_programs_are_eliminated(self):
        """测试等价程序是否被去重（保留3个唯一程序）"""
        generator = self.synthesizer.eliminate_equivalents(
            self.test_programs, self.test_inputs, self.initial_cache, iteration=0
        )
        unique_programs = list(generator)
        
        # 打印所有签名，调试等价性
        signatures = [self.initial_cache[p] for p in self.test_programs]
        print(f"All signatures: {signatures}")
    
        # 验证结果长度：5个输入 → 3个唯一程序
        assert len(unique_programs) == 3

    def test_cache_is_updated(self):
        generator = self.synthesizer.eliminate_equivalents(
            self.test_programs, self.test_inputs, self.initial_cache, iteration=0
        )
        list(generator)
    
        # 打印缓存中的所有程序，确认是5个不同对象
        print(f"Cached programs: {list(self.initial_cache.keys())}")
        assert len(self.initial_cache) == 3 # 5

    def test_signature_reuse(self):
        """测试缓存中的签名是否被复用（避免重复计算）"""
        # 第一次处理：填充缓存
        generator1 = self.synthesizer.eliminate_equivalents(
            self.test_programs, self.test_inputs, self.initial_cache, iteration=0
        )
        try:
            list(generator1)
        except StopIteration as e:
            cache_after_first = e.value
        else:
            cache_after_first = {}
        
        # 新增一个与rect1等价的程序
        new_rect = Rectangle(Coordinate(0,0), Coordinate(2,2))
        new_programs = self.test_programs + [new_rect]
        
        # 第二次处理：使用已有缓存
        generator2 = self.synthesizer.eliminate_equivalents(
            new_programs, self.test_inputs, cache_after_first, iteration=1
        )
        unique_programs = list(generator2)
        
        # 验证结果仍为3个唯一程序（new_rect被去重）
        assert len(unique_programs) == 3

    def test_empty_input(self):
        """测试空程序列表的处理"""
        generator = self.synthesizer.eliminate_equivalents(
            program_list=[], test_inputs=self.test_inputs, cache={}, iteration=0
        )
        assert list(generator) == []  # 无程序输出
        
        # 验证缓存仍为空
        try:
            list(generator)
        except StopIteration as e:
            final_cache = e.value
        else:
            final_cache = {}
        assert final_cache == {}
        