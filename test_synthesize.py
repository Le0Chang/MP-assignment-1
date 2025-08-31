import pytest
import numpy as np
from enumerative_synthesis import BottomUpSynthesizer
from shapes import Shape, Rectangle, Circle, Union, Coordinate, ShapeVisualizer

# 1. 实现具体的形状合成器（继承抽象类）
class ShapeSynthesizer(BottomUpSynthesizer[Shape]):
    """针对几何形状的具体合成器，实现抽象方法"""
    def generate_terminals(self, examples: List[np.ndarray]) -> List[Shape]:
        """生成终端程序：所有可能的基础形状（矩形、圆）"""
        terminals = []
        # 生成矩形（顶点坐标范围 0-5）
        for x1 in range(6):
            for y1 in range(6):
                for x2 in range(x1+1, 6):
                    for y2 in range(y1+1, 6):
                        terminals.append(Rectangle(Coordinate(x1, y1), Coordinate(x2, y2)))
        # 生成圆（圆心坐标 0-5，半径 1-3）
        for cx in range(6):
            for cy in range(6):
                for r in range(1, 4):
                    terminals.append(Circle(Coordinate(cx, cy), r))
        return terminals
    
    def grow(self, program_list: List[Shape], examples: List[np.ndarray]) -> List[Shape]:
        """生长程序：对现有程序应用组合操作（并集、交集）"""
        grown = []
        # 对所有程序对应用 Union 和 Intersection
        for p1 in program_list:
            for p2 in program_list:
                if p1 != p2:  # 避免自组合（可选优化）
                    grown.append(Union(p1, p2))
                    # grown.append(Intersection(p1, p2))  # 可按需添加更多操作
        return grown
    
    def is_correct(self, program: Shape, examples: List[np.ndarray]) -> bool:
        """验证程序是否满足所有示例（输入点是否在形状内）"""
        xs, ys, expected = examples  # 示例格式：(x坐标, y坐标, 预期输出)
        actual = program.interpret(xs, ys)
        return np.array_equal(actual, expected)
    
    def extract_test_inputs(self, examples: List[np.ndarray]) -> List[Any]:
        """从示例中提取测试点（用于等价性消除）"""
        xs, ys, _ = examples
        return [(xs, ys)]  # 返回 (x坐标, y坐标) 作为测试输入
    
    def compute_signature(self, program: Shape, test_inputs: List[Any]) -> Any:
        """计算程序在测试点上的签名（输出布尔值 tuple）"""
        xs, ys = test_inputs[0]
        return tuple(program.interpret(xs, ys))


# 2. 测试用例：定义输入输出示例
def create_rectangle_example():
    """示例1：目标是 Rectangle(0,0,2,2)"""
    xs = np.array([0, 1, 2, 3])  # 测试点 x 坐标
    ys = np.array([0, 1, 2, 3])  # 测试点 y 坐标
    expected = np.array([True, True, True, False])  # 点是否在矩形内
    return (xs, ys, expected)

def create_union_example():
    """示例2：目标是 Union(Rectangle(0,0,2,2), Circle(3,3,1))"""
    xs = np.array([1, 3, 4])
    ys = np.array([1, 3, 4])
    expected = np.array([True, True, False])  # 前两点在 union 内
    return (xs, ys, expected)


# 3. 测试类
class TestSynthesize:
    def setup_method(self):
        self.synthesizer = ShapeSynthesizer()
        self.visualizer = ShapeVisualizer(output_dir="test_visualizations")  # 可视化结果
    
    def test_synthesize_rectangle(self):
        """测试合成简单矩形"""
        example = create_rectangle_example()
        program = self.synthesizer.synthesize([example], max_iterations=1)
        
        # 验证结果是正确的矩形
        assert isinstance(program, Rectangle)
        assert program.bottom_left == Coordinate(0, 0)
        assert program.top_right == Coordinate(2, 2)
        
        # 可视化结果（可选）
        self.visualizer.visualize_test_case(
            example[0], example[1], example[2], "rectangle_test", program
        )
    
    def test_synthesize_union(self):
        """测试合成形状的并集（需要生长迭代）"""
        example = create_union_example()
        program = self.synthesizer.synthesize([example], max_iterations=2)
        
        # 验证结果是正确的并集
        assert isinstance(program, Union)
        # 验证并集的两个子形状
        assert (isinstance(program.first, Rectangle) and 
                program.first.bottom_left == Coordinate(0, 0) and 
                program.first.top_right == Coordinate(2, 2))
        assert (isinstance(program.second, Circle) and 
                program.second.center == Coordinate(3, 3) and 
                program.second.radius == 1)
        
        # 可视化结果（可选）
        self.visualizer.visualize_test_case(
            example[0], example[1], example[2], "union_test", program
        )
    
    def test_no_solution(self):
        """测试无解决方案的场景（应抛出异常）"""
        # 定义一个不可能满足的示例（如点 (0,0) 既在形状内又在形状外）
        impossible_example = (
            np.array([0]), 
            np.array([0]), 
            np.array([True, False])  # 矛盾的预期
        )
        with pytest.raises(ValueError, match="No program found"):
            self.synthesizer.synthesize([impossible_example], max_iterations=1)
            