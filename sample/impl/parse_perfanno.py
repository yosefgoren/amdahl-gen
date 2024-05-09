#!/bin/pypy3
from lark import Lark
from lark.tree import Tree

def _tree_to_json(tree):
    if isinstance(tree, Tree):
        return {tree.data: [_tree_to_json(c) for c in tree.children]}
    else:
        return str(tree)

def _unshell(tgt: list):
    return tgt[0]

def _strsum(tgt: list):
    return 0.0 + sum(float(num) for num in tgt) # initial 0.0 ensures float result

def _process_json_tree(jtree):
    return [{key: aggregator(srcline["srcline"][i][key]) for i, (key, aggregator) in enumerate([("lineno", _unshell), ("linetxt", _unshell), ("runtime", _strsum)])} for srcline in jtree["start"]]

def parse_peranno_txt(text: str) -> object:
    parser = Lark(
    '''start: _line*

        _line: _emptyrow
            | _perc
            | _seperator
            | srcline 

        _perc: "Percent |" _SUFFIX
        _seperator: "---------------------" _SUFFIX    
        
        srcline: _srcrow runtime

        runtime: _srccont*
        
        _srccont:
            | _asmrow
            | _emptyrow

        _srcrow: ":" lineno linetxt
        _asmrow: FLOAT ":" _HEXNUM _SUFFIX
        _emptyrow: ":"

        lineno: NUMBER
        linetxt: /.+/
        
        _SUFFIX: /.+/

        _HEXNUM: /[0-9a-fA-F]+/

    %import common.WORD
    %import common.NUMBER
    %import common.FLOAT
    %ignore /\s+/
    ''')

    parsed = parser.parse(text)
    full_jtree = _tree_to_json(parsed)
    return _process_json_tree(full_jtree)