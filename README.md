# neO-DCN - Network Optimizer for Data Center Networks by Portfolio Solving

neO-DCN is a solver is able to run several kinds of solvers, such as ILP solvers, in parallel to solve optimization problems over data center networks (DCNs).
neO is able not only to interface to several solvers such as Gurobi, SCIP, CP-SAT, etc., but also to encode the instances of the optimization problem and the DCN constraints as ILP instances.

## License

neO-DCN is under GPL license, check out the COPYING file.
In essence you can not distribute a program that uses this version unless you make your program available under GPL as well. 
If you need another license in order to use our software as part of a program which is not going to be distributed under GPL, please contact
Gergely Kovasznai <kovasznai.gergely@uni-eszterhazy.hu>.

If you want neO-DCN to execute Gurobi as an ILP solver, you need to purchase a Gurobi license, which is free for academics and 
students: https://www.gurobi.com/academia/academic-program-and-licenses/

## Installation

neO requires Python 3.

```
pip install parse pathos ortools gurobipy
```

If you want neO-DCN to execute Gurobi as an ILP solver, follow installation instructions at https://www.gurobi.com/documentation/9.1/quickstart_linux/software_installation_guid.html#section:Installation

## Command-line usage

To find out command-line usage, use the command-line argument `--help`:
```
python neO.py --help
```

Command-line arguments regarding solvers:
- `--or-solver`: to run OR-Tools ILP solver such as SCIP, CBC, Gurobi.
- `--cp-solver`: to run CP-SAT, providing native support for indicator constraints.
- `--gurobi-solver`: to run Gurobi via the package gurobipy, providing native support for indicator constraints.

Command-line arguments regarding the results:
- `--get-scheduling`: to retrieve an optimal scheduling of the sensor nodes.
<!-- - `--verify-scheduling`: to verify if the resulting scheduling satisfies the WSN constraints. -->
- `--timeout`: to set the timeout in seconds.

## Benchmarks

Benchmarks are provided in the folder <code>benchmarks</code>, in JSON format. The <code>version</code> attribute corresponds to the DCN model to be used:
* <code>version: 1</code>: DCN model with traffic consolidation to minimize the number of active links
* <code>version: 2</code>: DCN model with traffic consolidation to minimize the number of active links and of active servers
* <code>version: 3</code>: DCN model with adaptive link speed to minimize the power consumption of links

Gergely Kovasznai, Eszterházy Károly Catholic University, Eger, Hungary, 2022.
