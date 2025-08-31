import pytest
from shapes import (
    Shape, Rectangle, Circle, Mirror,
    Union, Intersection, Subtraction, Coordinate
)
from shape_synthesizer import ShapeSynthesizer

# 辅助函数：创建测试用的基础形状
def create_test_shapes():
    coord1 = Coordinate(0, 0)
    coord2 = Coordinate(2, 2)
    rect = Rectangle(coord1, coord2)  # 矩形：左下角(0,0)，右上角(2,2)
    circle = Circle(coord1, 1)  # 圆：中心(0,0)，半径1
    return [rect, circle]

class TestShapeSynthesizerGrow:
    def setup_method(self):
        # 初始化合成器实例
        self.synthesizer = ShapeSynthesizer()
        # 测试用的基础程序列表（2个形状）
        self.base_programs = create_test_shapes()
        # 空程序列表（用于边界测试）
        self.empty_programs = []

    def test_grow_preserves_original_programs(self):
        """测试grow是否保留原始程序"""
        grown = self.synthesizer.grow(self.base_programs, examples=[])
        # 原始程序必须全部包含在结果中
        for p in self.base_programs:
            assert p in grown

    def test_grow_generates_mirror_operations(self):
        """测试是否生成了所有Mirror操作"""
        grown = self.synthesizer.grow(self.base_programs, examples=[])
        # 对每个原始程序，检查是否存在对应的Mirror实例
        for p in self.base_programs:
            mirror_p = Mirror(p)
            assert mirror_p in grown

    def test_grow_generates_binary_operations(self):
        """测试是否生成了所有双目操作（Union/Intersection/Subtraction）"""
        grown = self.synthesizer.grow(self.base_programs, examples=[])
        # 遍历所有程序对，检查三种双目操作是否存在
        for p1 in self.base_programs:
            for p2 in self.base_programs:
                assert Union(p1, p2) in grown
                assert Intersection(p1, p2) in grown
                assert Subtraction(p1, p2) in grown

    def test_grow_removes_duplicates(self):
        """测试是否去除了重复程序"""
        # 创建包含重复元素的输入列表
        duplicate_programs = self.base_programs + [self.base_programs[0]]
        grown = self.synthesizer.grow(duplicate_programs, examples=[])
        # 去重后，原始程序的重复项应被合并（通过计算长度验证）
        # 原始去重后长度为2，grow后新增的程序数应固定，不受重复输入影响
        unique_base = list(set(duplicate_programs))
        grown_from_unique = self.synthesizer.grow(unique_base, examples=[])
        assert len(grown) == len(grown_from_unique)

    def test_grow_with_empty_input(self):
        """测试空输入列表的处理"""
        grown = self.synthesizer.grow(self.empty_programs, examples=[])
        # 空输入应返回空列表（无原始程序，也无法生成新程序）
        assert grown == []

    def test_grow_output_length(self):
        """测试输出长度是否符合预期（验证操作生成的完整性）"""
        n = len(self.base_programs)  # 基础程序数量：2
        # 预期新增的程序数：
        # - 单目操作：n个（每个程序生成1个Mirror）
        # - 双目操作：n*n*3个（每个程序对生成3种操作）
        # 总长度 = 原始程序数(n) + 单目操作数(n) + 双目操作数(3n²)
        expected_length = n + n + 3 * n * n
        grown = self.synthesizer.grow(self.base_programs, examples=[])
        assert len(grown) == expected_length
        