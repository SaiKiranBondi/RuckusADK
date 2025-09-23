import ast
from typing import Any, Dict, List, Union
from pycparser import c_parser, c_ast

# This class is a visitor that walks the Abstract Syntax Tree (AST) of the Python code.
class CodeVisitor(ast.NodeVisitor):
    """
    Visits nodes in an AST to extract information about classes and functions.
    """
    def __init__(self):
        self.structure: List[Dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        """Called when the visitor finds a class definition."""
        class_info = {
            "type": "class",
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "methods": []
        }
        
        # Iterate through the body of the class to find method definitions
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._get_function_details(item)
                class_info["methods"].append(method_info)
        
        self.structure.append(class_info)
        # We don't call generic_visit here to avoid visiting methods twice.

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Called when the visitor finds a function definition at the top level.
        It ignores methods inside classes, which are handled by visit_ClassDef.
        """
        # We check if the function's parent is a Module, which means it's a top-level function.
        # This requires walking the tree with parent pointers or a simpler check.
        # For simplicity here, we'll assume the main function will call this for top-level nodes.
        # A more robust implementation would track the parent node.
        # Let's assume the main function logic prevents double-counting for now.
        if not any(isinstance(parent, ast.ClassDef) for parent in getattr(node, 'parents', [])):
             func_info = self._get_function_details(node)
             func_info["type"] = "function"
             self.structure.append(func_info)

    def _get_function_details(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Helper to extract details from any function or method node."""
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "parameters": [
                {
                    "name": arg.arg,
                    # ast.unparse is a clean way to get the string representation of a type hint
                    "annotation": ast.unparse(arg.annotation) if arg.annotation else None
                }
                for arg in node.args.args
            ],
            "return_type": ast.unparse(node.returns) if node.returns else None
        }

# C-specific analysis classes and functions
class CCodeVisitor(c_ast.NodeVisitor):
    """
    Visits nodes in a C AST to extract information about functions and structures.
    """
    def __init__(self):
        self.structure: List[Dict[str, Any]] = []

    def visit_FuncDef(self, node: c_ast.FuncDef):
        """Called when the visitor finds a function definition."""
        func_info = {
            "type": "function",
            "name": node.decl.name,
            "parameters": [],
            "return_type": self._get_type_string(node.decl.type.type)
        }
        
        # Extract parameters
        if node.decl.type.args:
            for param in node.decl.type.args.params:
                if isinstance(param, c_ast.Decl):
                    param_info = {
                        "name": param.name,
                        "type": self._get_type_string(param.type)
                    }
                    func_info["parameters"].append(param_info)
        
        self.structure.append(func_info)

    def visit_Typedef(self, node: c_ast.Typedef):
        """Called when the visitor finds a typedef (structure definition)."""
        if isinstance(node.type, c_ast.Struct):
            struct_info = {
                "type": "struct",
                "name": node.name,
                "fields": []
            }
            
            # Extract struct fields
            if node.type.decls:
                for field in node.type.decls:
                    if isinstance(field, c_ast.Decl):
                        field_info = {
                            "name": field.name,
                            "type": self._get_type_string(field.type)
                        }
                        struct_info["fields"].append(field_info)
            
            self.structure.append(struct_info)

    def _get_type_string(self, type_node: c_ast.Node) -> str:
        """Convert AST type node to string representation."""
        if isinstance(type_node, c_ast.TypeDecl):
            return self._get_type_string(type_node.type)
        elif isinstance(type_node, c_ast.IdentifierType):
            return ' '.join(type_node.names)
        elif isinstance(type_node, c_ast.PtrDecl):
            return f"{self._get_type_string(type_node.type)}*"
        elif isinstance(type_node, c_ast.ArrayDecl):
            return f"{self._get_type_string(type_node.type)}[]"
        else:
            return "unknown"

def analyze_c_code_structure(source_code: str) -> Dict[str, Any]:
    """
    Parses C source code into a structured JSON representation.
    
    Args:
        source_code: The C source code to be analyzed as a string.
        
    Returns:
        A JSON-serializable dictionary representing the C code structure.
    """
    try:
        # Create parser
        parser = c_parser.CParser()
        
        # Parse the code
        ast = parser.parse(source_code)
        
        # Visit the AST
        visitor = CCodeVisitor()
        visitor.visit(ast)
        
        return {
            "status": "success", 
            "structure": visitor.structure
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"C parsing error: {e}"
        }

def analyze_code_structure(source_code: str, language: str) -> Dict[str, Any]:
    """
    Parses source code into a structured JSON representation of its AST.
    
    This tool provides a detailed breakdown of classes, methods, function signatures,
    parameters, type hints, return types, and docstrings.
    
    Args:
        source_code: The source code to be analyzed as a string.
        language: The programming language of the source code (e.g., 'python', 'c').
        
    Returns:
        A JSON-serializable dictionary representing the code structure.
    """
    if language.lower() == 'python':
        try:
            tree = ast.parse(source_code)
            visitor = CodeVisitor()
            visitor.visit(tree)
            return {"status": "success", "structure": visitor.structure}
        except SyntaxError as e:
            return {"status": "error", "message": f"Python syntax error: {e}"}
    
    elif language.lower() == 'c':
        # Use local C analysis function
        return analyze_c_code_structure(source_code)
    
    else:
        return {"status": "error", "message": f"Unsupported language: {language}"}