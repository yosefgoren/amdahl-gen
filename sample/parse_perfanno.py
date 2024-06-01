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

def try_parse_lineno(txt: str) -> int:
    res = None
    try:
        res = int(txt)-5
    except Exception:
        pass
    if res is None or res < 0:
        raise Exception(f"failed parsing supposed lineno (must be int > 4):\n\t{txt}")
    return res

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
                "lineno": try_parse_lineno(srcline[0]["lineno"][0]),
                "linetxt": srcline[1]["linetxt"][0],
                "event_count": _strsum(srcline[2]["event_count"]),
            })
        results.append(res)
    
    
    # create cycle and instruction counters for each line of source code:
    byline = {lineno: {"lineno": lineno, "cycle_count": 0, "instr_count": 0, "linetxt": None} for lineno in linenos}
    # extract cycle counters and text:
    for entry in cycle_container:
        target = byline[entry["lineno"]]
        target["cycle_count"] += entry["event_count"]
        target["linetxt"] = entry["linetxt"]

    # extract instruction counters, and match text:
    for entry in instr_container:
        target = byline[entry["lineno"]]
        target["instr_count"] += entry["event_count"]
        _assert_eq_or_none(target["linetxt"], entry["linetxt"])
        target["linetxt"] = entry["linetxt"]

    return list(byline.values())


PERFANNO_PARSER =  Lark(
    '''start: section*
        section: _perc _seperator ":" ":" ":" _line_disassembly_of ":" _line_addr_sym _line_name_sym srcline*

        _perc: "Period" "|" "Source code & Disassembly of" filepath "for" linetxt
        _seperator: "------------------" _SUFFIX    
        _line_disassembly_of: ":" _DECNUM "Disassembly of section" _SUFFIX
        _line_addr_sym: ":" _DECNUM _HEXNUM "<" _SUFFIX
        _line_name_sym: ":" _DECNUM _SYMBOL
        

        srcline: _srctext event_count |

        event_count: _srccont*
        
        _srccont:
            | _asmrow
            | _emptyrow

        _srctext: ":" lineno linetxt
        _asmrow: NUMBER ":" _HEXNUM _SUFFIX
        _emptyrow: ":"

        linetxt: /.+/

        filepath: /[0-9a-zA-Z_\-\/\.]+/
        
        _SUFFIX: /.+/

        _HEXNUM: /[0-9a-fA-F]+/

        _DECNUM: /[0-9]+/

        lineno: /[0-9]+/

        _SYMBOL: /[0-9a-zA-Z_\.]+\(.*\):/

    %import common.WORD
    %import common.NUMBER
    %import common.FLOAT
    %ignore /\s+/
    ''')

def parse_clean_perfanno(text: str) -> object:
    try:
        parsed = PERFANNO_PARSER.parse(text)
    except Exception as e:
        print(f"parsing annotated failed. ensure compiling with -g flag. error was:\n\t{e}")
        raise e
    full_jtree = _tree_to_json(parsed)
    with open('tmp.json', 'w') as f:
        json.dump(full_jtree, f, indent=4)
    return _process_json_tree(full_jtree)

def parse_section_delims(text: str) -> list:
    lines = text.splitlines()
    delim_indices = [idx for idx, line in enumerate(lines) if line.startswith('----------------------')]
    delim_indices.append(len(lines)+1)
    sections = []
    for meta_idx, start_delim_idx in enumerate(delim_indices[:-1]):
        end_delim_idx = delim_indices[meta_idx+1]
        if start_delim_idx < 1:
            raise Exception('perf annotation in bad format. section delimiter "-----..." as first line')
        title = lines[start_delim_idx-1]
        header = lines[start_delim_idx+1:start_delim_idx+7]
        content = lines[start_delim_idx+7:end_delim_idx-1]
        sections.append((title, header, content))
    return sections

TITLE_PATTERN = re.compile("\s+Period\s+\|\s+Source code & Disassembly of\s+([^\s]+)\s+for\s+([^\s]+).*")
SECTION_HEADER_PATTERN = re.compile("\s+:\s+[0-9]+\s+Disassembly of section\s+([^\s]+):\s*")

def _starts_with_noneof(txt: str, prefixes: list) -> bool:
    return all([not txt.startswith(prefix) for prefix in prefixes])

def is_section_relevant(title: str, header: list):
    m = TITLE_PATTERN.fullmatch(title)
    if m is None:
        raise Exception(f"Failed to interpret section title (not match pattern):\n\t'{title}'")
    fname, target = m.groups()

    m = SECTION_HEADER_PATTERN.fullmatch(header[3])
    if m is None:
        raise Exception(f"Failed to interpret section header (not match pattern):\n\t'{header[3]}'")
    section_name, = m.groups()

    return _starts_with_noneof(fname, [
        "libgomp.so",
        "ld-linux",
        "libc.so",
        "libm.so",
    ]) and _starts_with_noneof(section_name, [
        ".plt"
    ])

def preprocess_perfanno(text: str) -> str:
    """preprocesses the annotation by removing sections which are not intresting to us, such as those dynamic linker and standard library, or .plt of the target code"""

    relevant_sections = [
        "\n".join([title, "-------------------------------------------------------------------------------------------------------------------"]+header+content)
        for title, header, content
        in parse_section_delims(text)
        if is_section_relevant(title, header)
    ]
    return "\n".join(relevant_sections)


def parse_peranno_txt(text: str) -> object:
    clean = preprocess_perfanno(text)
    with open('perfanno.clean.txt', 'w') as f:
        f.write(clean)
    return (parse_clean_perfanno(clean))
        
    