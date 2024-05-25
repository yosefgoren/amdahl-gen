#!/bin/pypy3
from lark import Lark
from lark.tree import Tree
import json
import re
from typeguard import typechecked

def _tree_to_json(tree):
    if isinstance(tree, Tree):
        return {tree.data: [_tree_to_json(c) for c in tree.children]}
    else:
        return str(tree)

def _unshell(tgt: list):
    return tgt[0]

def _derefint(tgt: list):
    return int(tgt[0])

def _strsum(tgt: list):
    return 0.0 + sum(float(num) for num in tgt) # initial 0.0 ensures float result

@typechecked
def is_section_linetxt(linetxt: str) -> bool:
    pattern = re.compile('[0-f]{16} <[a-z0-9_@\.]+>:')
    return pattern.fullmatch(linetxt.strip()) is not None

def _process_json_tree(jtree):
    process_handlers = [
        ("lineno", _derefint),
        ("linetxt", _unshell),
        ("runtime", _strsum),
    ]
    
    res = [{
                key: aggregator(srcline["srcline"][i][key])
            for i, (key, aggregator)
            in enumerate(process_handlers)
        }
        for srcline
        in jtree["start"]
        if len(srcline["srcline"][2]["runtime"]) > 0
            and not is_section_linetxt(srcline["srcline"][1]["linetxt"][0])
    ]
    for d in res:
        d["times_executed"] = 1
    return res

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
    with open('tmp.json', 'w') as f:
        json.dump(full_jtree, f, indent=4)
    return _process_json_tree(full_jtree)