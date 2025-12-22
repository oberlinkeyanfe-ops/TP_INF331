import ast, sys
p='Backend/routes/dashboard.py'
try:
    s=open(p,'r',encoding='utf8').read()
    ast.parse(s)
    print('AST OK')
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
