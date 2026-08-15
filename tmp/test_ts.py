import sys
import os
import site

# Try to find user site-packages if not in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.append(user_site)

from tree_sitter import Language, Parser
import tree_sitter_typescript as tsts
import tree_sitter_rust as tsrust
import tree_sitter_go as tsgo

LANG_TS = Language(tsts.language_typescript())
LANG_RS = Language(tsrust.language())
LANG_GO = Language(tsgo.language())

def dump(lang, code):
    parser = Parser(lang)
    tree = parser.parse(code.encode('utf8'))
    print(tree.root_node.sexp())

print("TS:")
dump(LANG_TS, "function foo(a: number): void { console.log(a); }")

print("RS:")
dump(LANG_RS, "fn foo(a: i32) -> () { println!(a); }")

print("GO:")
dump(LANG_GO, "func foo(a int) { fmt.Println(a) }")
