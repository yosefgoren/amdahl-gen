import re

p = re.compile("\s+:\s+[0-9]+\s+Disassembly of section\s+([^\s]+):\s*")
# p = re.compile("\s+:\s+[0-9]+\s+Disassembly of section\s+([^\s]+).+")
t = '             : 3    Disassembly of section .text:'
print(p.match(t))
print(p.fullmatch(t))