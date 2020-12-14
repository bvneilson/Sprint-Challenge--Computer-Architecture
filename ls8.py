import sys
from cpu import *

if len(sys.argv) != 2:
    print("Usage: ls8.py 'valid file path'")

else:
    try:
        cpu = CPU()

        cpu.load(sys.argv[1])
        cpu.run()

    except FileNotFoundError:
        print(f"Couldn't open {sys.argv[1]}")
