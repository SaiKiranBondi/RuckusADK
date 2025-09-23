import re
from typing import Any, Dict, List, Union
from pycparser import c_parser, c_ast

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
