# Timber

A programming language that I wrote some time ago.

Programs are run on a virtual machine implemented in ./timber/vm.py.

`./code.timber` is the hello world program written in timber. To run it, run:

    ./main.py run code.timber

Alternatively, run one of:

    ./main.py lex code.timber
    ./main.py ast code.timber
    ./main.py asm code.timber

... To print the tokens, Abstract Syntax tree and Assembly of the code.timber
program respectively.
