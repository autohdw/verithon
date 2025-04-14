import ast
import inspect
from astunparse import unparse

import ast
import inspect
from collections import defaultdict

import ast
import inspect

import ast
import inspect
from astunparse import unparse


def find_irrelevant_line_in_for_loop(func):
    source = inspect.getsource(func)
    tree = ast.parse(source)
    function_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

    # 查找所有最内层for循环（多个并列情况）
    class ForLoopAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.for_nodes = []  # 所有for循环节点
            self.depth_map = {}  # 节点到深度的映射
            self.current_depth = 0  # 当前遍历深度
            self.max_depth = 0  # 全函数最大循环深度

        def visit_For(self, node):
            self.current_depth += 1
            self.depth_map[node] = self.current_depth
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)  # 遍历子节点处理嵌套
            self.current_depth -= 1
            self.for_nodes.append(node)

    analyzer = ForLoopAnalyzer()
    analyzer.visit(function_def)

    # 筛选所有深度等于最大深度的循环（可能多个）
    inner_for_nodes = [
        node for node in analyzer.for_nodes
        if analyzer.depth_map.get(node, 0) == analyzer.max_depth
    ]

    irrelevant_lines = []

    # 对每个最内层循环独立分析
    for for_node in inner_for_nodes:
        lines_in_single_for_node = []
        # 收集循环体内赋值的变量（含循环变量）
        assigned_vars = set()

        # 添加循环变量（如for i中的i）
        def add_loop_vars(target):
            if isinstance(target, ast.Name):
                assigned_vars.add(target.id)
            elif isinstance(target, ast.Tuple):
                for elt in target.elts:
                    add_loop_vars(elt)

        add_loop_vars(for_node.target)

        # 收集显式赋值的变量
        class AssignmentCollector(ast.NodeVisitor):
            def __init__(self):
                self.assigned = set()

            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.assigned.add(target.id)

            def visit_AugAssign(self, node):
                if isinstance(node.target, ast.Name):
                    self.assigned.add(node.target.id)

        collector = AssignmentCollector()
        collector.visit(for_node)
        assigned_vars.update(collector.assigned)

        # 分析函数调用
        for stmt in for_node.body:
            if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
                continue

            call = stmt.value
            # 检查函数名是否以Module开头
            func_name = ""
            if isinstance(call.func, ast.Name):
                func_name = call.func.id
            elif isinstance(call.func, ast.Attribute):
                func_name = call.func.attr
            else:
                continue
            if not func_name.startswith("Module"):
                continue

            # 收集非PORTS参数
            args_to_check = list(call.args)
            for kw in call.keywords:
                if kw.arg != "PORTS":
                    args_to_check.append(kw.value)

            # 检查参数是否依赖循环内变量
            is_irrelevant = True
            for arg in args_to_check:
                class VarCollector(ast.NodeVisitor):
                    def __init__(self):
                        self.vars = set()

                    def visit_Name(self, node):
                        if isinstance(node.ctx, ast.Load):
                            self.vars.add(node.id)

                collector = VarCollector()
                collector.visit(arg)
                if assigned_vars & collector.vars:
                    is_irrelevant = False
                    break

            if is_irrelevant:
                line = unparse(stmt).strip()
                if line not in irrelevant_lines:  # 避免重复
                    # irrelevant_lines.append(line)
                    lines_in_single_for_node.append(stmt.lineno)

        irrelevant_lines.append(lines_in_single_for_node)

    return irrelevant_lines


import ast
import inspect


def find_irrelevant_line_in_for_loop_new(func):
    source = inspect.getsource(func)
    tree = ast.parse(source)
    function_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

    # 添加父节点记录
    class ParentVisitor(ast.NodeVisitor):
        def __init__(self):
            self.parent_map = {}

        def visit(self, node):
            for child in ast.iter_child_nodes(node):
                self.parent_map[child] = node
                self.visit(child)

    parent_visitor = ParentVisitor()
    parent_visitor.visit(function_def)
    parent_map = parent_visitor.parent_map

    # 查找所有最内层for循环
    class ForLoopAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.for_nodes = []
            self.depth_map = {}
            self.current_depth = 0
            self.max_depth = 0

        def visit_For(self, node):
            self.current_depth += 1
            self.depth_map[node] = self.current_depth
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
            self.for_nodes.append(node)

    analyzer = ForLoopAnalyzer()
    analyzer.visit(function_def)

    inner_for_nodes = [
        node for node in analyzer.for_nodes
        if analyzer.depth_map.get(node, 0) == analyzer.max_depth
    ]

    irrelevant_lines = []

    # 收集循环变量的辅助函数
    def add_loop_vars(target, var_set):
        if isinstance(target, ast.Name):
            var_set.add(target.id)
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                add_loop_vars(elt, var_set)

    # 显式赋值收集器
    class AssignmentCollector(ast.NodeVisitor):
        def __init__(self):
            self.assigned = set()

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.assigned.add(target.id)

        def visit_AugAssign(self, node):
            if isinstance(node.target, ast.Name):
                self.assigned.add(node.target.id)

    # 对每个最内层循环分析其内部语句
    for for_node in inner_for_nodes:
        for stmt in for_node.body:
            if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
                continue

            call = stmt.value
            # 检查函数名是否以Module开头
            func_name = ""
            if isinstance(call.func, ast.Name):
                func_name = call.func.id
            elif isinstance(call.func, ast.Attribute):
                func_name = call.func.attr
            else:
                continue
            if not func_name.startswith("Module"):
                continue

            # 获取该语句所属的所有父For循环
            parent_for_nodes = []
            current = stmt
            while True:
                current = parent_map.get(current)
                if current is None:
                    break
                if isinstance(current, ast.For):
                    parent_for_nodes.append(current)

            # 收集所有父循环中的变量
            assigned_vars = set()
            for parent_for in parent_for_nodes:
                # 添加循环变量
                add_loop_vars(parent_for.target, assigned_vars)
                # 收集显式赋值
                collector = AssignmentCollector()
                collector.visit(parent_for)
                assigned_vars.update(collector.assigned)

            # 检查参数是否依赖这些变量
            args_to_check = list(call.args)
            for kw in call.keywords:
                if kw.arg != "PORTS":
                    args_to_check.append(kw.value)

            is_irrelevant = True
            for arg in args_to_check:
                class VarCollector(ast.NodeVisitor):
                    def __init__(self):
                        self.vars = set()

                    def visit_Name(self, node):
                        if isinstance(node.ctx, ast.Load):
                            self.vars.add(node.id)

                collector = VarCollector()
                collector.visit(arg)
                if assigned_vars & collector.vars:
                    is_irrelevant = False
                    break

            if is_irrelevant:
                irrelevant_lines.append(stmt.lineno)

    return irrelevant_lines

def ModuleTest1(a,b):
    return a+b

def ModuleTest2(a,**kwargs):
    return a

def ModuleTest3(a, c=30):
    return c

def ModuleTest4(d):
    return d
# 测试函数
def sample_func():
    a = 10
    b = 20
    for j in range(100):
        f = j + 1
        ModuleTest1(2,3)# 外层循环
        for i in range(50):
            # 最内层循环
            m = i+2
            k = m*4
            ModuleTest1(a, b)
            # 符合条件
            ModuleTest2(f, PORTS=j)
            # i变化，不符合
            ModuleTest3(a, c=30)          # 符合条件（假设c在外部定义且不变）
            d = 40
            ModuleTest4(d)                # d在循环内被赋值，不符合

    for k in range(1000):
        for l in range(200):
            ModuleTest1(1,2)
# 执行检测
print(find_irrelevant_line_in_for_loop_new(sample_func))
# 输出结果示例：
# ['ModuleTest1(a, b)', 'ModuleTest3(a, c=30)']
