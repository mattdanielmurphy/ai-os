import sys, site
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.append(user_site)

from tree_sitter import Language, Parser
import tree_sitter_typescript as tsts

LANG_TS = Language(tsts.language_typescript())

code = "function foo(a: number): void {\n  console.log(a);\n}\nclass Bar {\n  baz() { return 1; }\n}"

parser = Parser(LANG_TS)
tree = parser.parse(code.encode('utf8'))

def replace_blocks(node, source_bytes):
    # node types that represent function bodies
    body_types = {"statement_block", "block"}
    function_types = {"function_declaration", "method_definition", "arrow_function", "function_item", "method_declaration", "func_literal"}
    
    replacements = []
    
    def visit(n):
        if n.type in body_types and n.parent and n.parent.type in function_types:
            replacements.append((n.start_byte, n.end_byte))
        else:
            for child in n.children:
                visit(child)
                
    visit(tree.root_node)
    
    replacements.sort(reverse=True)
    res = bytearray(source_bytes)
    for start, end in replacements:
        res[start:end] = b"{ ... }"
        
    return res.decode('utf8')

print(replace_blocks(tree.root_node, code.encode('utf8')))
