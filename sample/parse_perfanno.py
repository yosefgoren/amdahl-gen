#!/bin/pypy3
from lark import Lark
from lark.tree import Tree
import json
import re
from typeguard import typechecked
from common.operators import map_byline

def _tree_to_json(tree):
    if isinstance(tree, Tree):
        return {tree.data: [_tree_to_json(c) for c in tree.children]}
    else:
        return str(tree)

def _strsum(tgt: list):
    return sum(int(num) for num in tgt)

@typechecked
def is_section_linetxt(linetxt: str) -> bool:
    pattern = re.compile('[0-f]{16} <[a-z0-9_@\.]+>:')
    return pattern.fullmatch(linetxt.strip()) is not None

def _assert_eq_or_none(target, value):
    if target is not None:
        if target != value:
            raise Exception(f"expected matching values: {target}, {value}")

def _process_json_tree(jtree):
    cycle_container = []
    instr_container = []

    sections_events = {
        "cpu_core/cycles": cycle_container,
        "cpu_core/instructions": instr_container,
    }

    results = []
    linenos = set()

    for section_c in jtree["start"]:
        section = section_c["section"]
        section_filepath = section[0]["filepath"][0]
        if "libc.so" in section_filepath:
            continue
        section_details = section[1]["linetxt"][0]
        container = None
        for event_key in sections_events.keys():
            if event_key in section_details:
                container = sections_events[event_key]
                break
        if container is None:
            # This section is not intresting ...
            continue
        res = []
        for lineno, srcline_c in enumerate(section[2:]):
            srcline = srcline_c["srcline"]
            linenos.add(lineno)
            container.append({
                "lineno": lineno,
                "linetxt": srcline[0]["linetxt"][0],
                "event_count": _strsum(srcline[1]["event_count"]),
            })
        results.append(res)
    
    
    byline = {lineno: {"lineno": lineno, "cycle_count": 0, "instr_count": 0, "linetxt": None} for lineno in linenos}
    for entry in cycle_container:
        target = byline[entry["lineno"]]
        target["cycle_count"] += entry["event_count"]
        target["linetxt"] = entry["linetxt"]

    for entry in instr_container:
        target = byline[entry["lineno"]]
        target["instr_count"] += entry["event_count"]
        _assert_eq_or_none(target["linetxt"], entry["linetxt"])
        target["linetxt"] = entry["linetxt"]

    return list(byline.values())

def parse_peranno_txt(text: str) -> object:
    parser = Lark(
    '''start: section*

        section: _perc _seperator ":" ":" ":" _line_disassembly_of ":" _line_addr_sym _line_name_sym srcline*

        _perc: "Period" "|" "Source code & Disassembly of" filepath "for" linetxt
        _seperator: "---------------------" _SUFFIX    
        _line_disassembly_of: ":" _DECNUM "Disassembly of section" _SUFFIX
        _line_addr_sym: ":" _DECNUM _HEXNUM "<" _SUFFIX
        _line_name_sym: ":" _DECNUM _SUFFIX
        
        srcline: _srcrow event_count |

        event_count: _srccont*
        
        _srccont:
            | _asmrow
            | _emptyrow

        _srcrow: ":" _DECNUM linetxt
        _asmrow: NUMBER ":" _HEXNUM _SUFFIX
        _emptyrow: ":"

        linetxt: /.+/

        filepath: /[a-zA-Z_\-\/\.]+/
        
        _SUFFIX: /.+/

        _HEXNUM: /[0-9a-fA-F]+/

        _DECNUM: /[0-9]+/

        _SYMBOL: /[0-9a-fA-F_]+/

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