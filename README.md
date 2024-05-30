# scl2ffl-transpiler
This project enables files written in Simple Circuit Language (SCL), a language formatted using S-expressions, to be transpiled into Finite Field Constraint Language (FFL) for the purposes of Zero Knowledge arithmetization. FFL requires that each constraint be as simple as possible (one multiplication symbol per line at max), and prevents the use of division and other non-standard operators. For more info about the syntax of these languages, please see [the original assignment](https://github.com/fredfeng/CS190-blockchain/tree/main/homework/hw4). The output FFL code is printed to the terminal.

# How to Run the Project
To run the program, use the following command:
```
python run.py [example_scl_file].scl
```
There are example input files in the `examples/` folder. For instance, if you want to transpile the `add.scl` file, use the following command.
```
python run.py examples/add.scl
```

# Code Organization
The Python file `run.py` intiates to transpilation process.

With the `scl/` folder, there are helper Python files to accomplish this task. `scl.py` and `ffl.py` contains useful classes to represent parts of the syntax of their respective languages, such as expressions, operators, and statements. `compile.py` (part of which was written by me) performs the recursive process of traversing through an abstract syntax tree of SCL and building up the abstract syntax of tree of FFL that represents the same equations but with FFL constraints.
