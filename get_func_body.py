def strip_comments(line):
    return line.split('//')[0] if '//' in line else line

def reterive_func_at(symbol: str, src_file_path: str, lineno: int) -> None | str:
    """
    Checks if a function named 'symbol' is defined in the source file at the provided line number.
    If so - returns the definition of the function (entire signature and body).
    Otherwise, returns 'None'.
    """
    with open(src_file_path, 'r') as file:
        lines = file.readlines()

    # Check if the line number is within the file
    if lineno > len(lines) or lineno < 1:
        return None

    function_code = []
    brace_count = 0

    first_line = lines[lineno-1].strip()
    if all(not token.startswith(symbol) for token in first_line.split(' ')) or not '{' in first_line:
        return None
    brace_count += first_line.count('{')
    brace_count -= first_line.count('}')
    
    while True:
        lineno += 1
        function_code.append(lines[lineno-1])
        current_line = strip_comments(lines[lineno-1])
        brace_count += current_line.count('{')
        brace_count -= current_line.count('}')
            
        if brace_count == 0:
            break

    return '\n'.join(function_code)


# def get_lineno(symbol: str, gelf_file_path: str)->None | int:
#     """
#     Checks if elf file has a DWARF section containing a symbol with the provided signature.
#     If so - returns the line number at which the definition can be found.
#     Otherwise, returns 'None'.
#     """
#     pass

def get_lineno(symbol: str, src_file_path: str)->None | int:
    lines = open(src_file_path, 'r').read().split('\n')
    for line_idx, line in enumerate(lines):
        if any(symbol in token for token in strip_comments(line).split(' ')):
            if ';' not in line and ('{' in line or '{' in lines[line_idx+1]):
                return line_idx+1
    return None

# def get_func_body(symbol: str, src_file_path: str, gelf_file_path: str)->str:
#     """
#         symbol: the name of a function such as 'foo'.
#         src_file_path: path to (C) source code where the function is defined.
#         gelf_file_path: an elf file of the source code which was compiled with '-g' file.
#     """
#     lineno = get_lineno(symbol, gelf_file_path)
#     if lineno is None:
#         raise Exception(f"Error: failed to find line number of symbol '{symbol}' in file '{gelf_file_path}'")
#     func = reterive_func_at(symbol, gelf_file_path, lineno)
#     if func is None:
#         raise Exception(f"Error: failed to find the function named '{symbol} in the file {src_file_path}' at line number '{lineno}'")
#     return func


def get_func_body(symbol: str, src_file_path: str)->str:
    """
        symbol: the name of a function such as 'foo'.
        src_file_path: path to (C) source code where the function is defined.
    """
    lineno = get_lineno(symbol, src_file_path)
    if lineno is None:
        raise Exception(f"Error: failed to find line number of function named '{symbol}' in file '{src_file_path}'")
    print(f"found at: {src_file_path}:{lineno}")
    func = reterive_func_at(symbol, src_file_path, lineno)
    if func is None:
        raise Exception(f"Error: failed to find the function named '{symbol}' at {src_file_path}:{lineno}'")
    return func