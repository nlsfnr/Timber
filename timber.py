#!/usr/bin/env python3
import argparse
from pathlib import Path

import vm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', metavar='CMD', type=str,
                        choices=['run', 'dbg', 'asm', 'ast', 'lex', 'tmp'])
    parser.add_argument('file', metavar='FILE', type=Path)
    args = parser.parse_args()

    file = args.file
    assert file.exists()

    with open(file, 'r') as fh:
        src = fh.read()

    if args.cmd == 'tmp':
        ops = [
            vm.Op(vm.OpKind.Push, 10),
            vm.Op(vm.OpKind.VStore, vm.to_ptr(1)),         # [_, 10]

            vm.Op(vm.OpKind.Call, 3),           # [rv, 10]
            vm.Op(vm.OpKind.Halt, 0),

            vm.Op(vm.OpKind.VIncr, vm.to_ptr(2)),
            vm.Op(vm.OpKind.VLoad, vm.to_ptr(-1)),
            vm.Op(vm.OpKind.VLoad, vm.to_ptr(-1)),
            vm.Op(vm.OpKind.Add, 0),
            vm.Op(vm.OpKind.VDecr, vm.to_ptr(2)),
            vm.Op(vm.OpKind.Ret, 0),
        ]
        m = vm.VM(ops)
        m.dbg()




if __name__ == '__main__':
    main()
