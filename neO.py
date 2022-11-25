# -*- coding: utf-8 -*-

import argparse
from enum import Enum
import glob
import os
import json
from time import time
from sys import stdout, exit
from math import pow, sqrt, ceil
import numpy
numpy.warnings.filterwarnings('ignore', category=numpy.VisibleDeprecationWarning)
import logging
logging.captureWarnings(True)

from models.model1 import DcnModel1
from models.model2 import DcnModel2

from solvers.card_enc_type import CardEncType, Relations, RelationOps
from solvers.solver import SolverResult, SolverResultType
from solvers.solver_sat import SatSolver, SatSolvers
from solvers.solver_smt import SmtSolver, SmtSolvers
# from solvers.solver_mip import MipSolver, MipSolvers
from solvers.solver_or import OrSolver, OrSolvers
from solvers.solver_cp import CpSat, CpSolvers
from solvers.solver_gurobi import GurobiSolver, GurobiSolvers


def runSolver(args):
	(solverType, dcnModel, getModel) = args

	if solverType in SatSolvers:
		solver = SatSolver(satSolverType=solverType, cardinalityEnc=cardinalityEnc, dumpFileName=dump_file)
	elif solverType in SmtSolvers:
		solver = SmtSolver(smtSolverType=solverType, dumpFileName=dump_file)
	elif solverType in OrSolvers:
		solver = OrSolver(orSolverType=solverType)
	elif solverType in CpSolvers:
		solver = CpSat()
	elif solverType in GurobiSolvers:
		solver = GurobiSolver()

	logging.info("{} starts encoding WSN...".format(solverType))
	outputVars = dcnModel.EncodeDcnConstraints(solver=solver)

	logging.info("{} starts solving...".format(solverType))
	isSAT = solver.solve()
	if isSAT == None:
		return

	result = SolverResult(solverType, isSAT = isSAT)
	if isSAT and getModel:
		result.model = solver.get_model(outputVars)

	del solver

	return result


def Optimize(dcnModel, getModel=False):
	from pathos.multiprocessing import ProcessPool
	from multiprocess.context import TimeoutError

	# wait for one of the solvers to finish
	solverConfigs = []
	if satSolverType:
		solverConfigs.extend([(solverType, dcnModel, getModel) for solverType in satSolverType])
	if smtSolverType:
		solverConfigs.extend([(solverType, dcnModel, getModel) for solverType in smtSolverType])
	if orSolverType:
		solverConfigs.extend([(solverType, dcnModel, getModel) for solverType in orSolverType])
	if cpSolverType:
		solverConfigs.extend([(solverType, dcnModel, getModel) for solverType in cpSolverType])
	if gurobiSolverType:
		solverConfigs.extend([(solverType, dcnModel, getModel) for solverType in gurobiSolverType])

	to = int(startTime + timeout - time()) if timeout else None
	pool = ProcessPool(len(solverConfigs), timeout=to)

	result = runSolver(solverConfigs[0])
	return result

	try:
		result = pool.uimap(runSolver, solverConfigs).next(timeout=to)
	except TimeoutError:
		result = SolverResult(isTIMEOUT = True)
	except:
		result = SolverResult()
	else:
		logging.info("Result provided by: {}".format(result.solverType))
		# if result.isSAT:
		# 	logging.info("SAT")
		# else:
		# 	logging.info("UNSAT")
	finally:
		pool.terminate()
		pool.clear()

	return result


# region Parse command line arguments-----------------------------------------------------------

parser = argparse.ArgumentParser("Generate optimal lifetime for sensor network by SAT and SMT solvers")

parser.add_argument("input_file", help="the input network file")

# parser.add_argument("--sat-solver",
# 					action="store", nargs='+', dest="sat_solver", default=["none"], type=str.lower,
# 					choices=[s.value for s in list(SatSolvers)] + ["none"],
# 					help="name(s) of SAT solvers (default: none)")
# parser.add_argument("--smt-solver",
# 					action="store", nargs='+', dest="smt_solver", default=["none"], type=str.lower,
# 					choices=[s.value for s in list(SmtSolvers)] + ["none"],
# 					help="name(s) of SMT solvers (default: none)")
parser.add_argument("--or-solver",
					action="store", nargs='+', dest="or_solver", default=["none"], type=str.lower,
					choices=[s.value for s in list(OrSolvers)] + ["none"],
					help="name(s) of ILP solvers by OR-Tools (default: none)")
parser.add_argument("--cp-solver",
					action="store_true", dest="cp_solver",
					help="run CP-SAT")
# parser.add_argument("--gurobi-solver",
# 					action="store_true", dest="gurobi_solver",
# 					help="run Gurobi")
parser.add_argument("--get-scheduling",
                    action="store_true", dest="bool_get_scheduling", default=False,
                    help="get the scheduling")
# parser.add_argument("--verify-scheduling",
#                     action="store_true", dest="bool_verify_scheduling", default=False,
#                     help="verify the scheduling")
# parser.add_argument("--dump-file",
#                     action="store", dest="dump_file",
#                     help="dump the intermediate DIMACS/SMT-LIB/etc. file, if applicable")
parser.add_argument("--log",
					action="store", dest="loglevel", default="ERROR", type=str.upper,
					choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
					help="logging level (default: ERROR)")
parser.add_argument("--timeout",
					action="store", type=int, dest="timeout", default=None,
					help="timeout for child processes in seconds")

args = parser.parse_args()

# endregion

# region Init constants and variables ---------------------------------------------------------------------

inputFile = args.input_file
bool_get_scheduling = args.bool_get_scheduling
# bool_verify_scheduling = args.bool_verify_scheduling

satSolverType = []
# for args_solver in args.sat_solver:
# 	if args_solver != "none": satSolverType.append(next(s for s in list(SatSolvers) if s.value == args_solver))

smtSolverType = []
# for args_solver in args.smt_solver:
# 	if args_solver != "none": smtSolverType.append(next(s for s in list(SmtSolvers) if s.value == args_solver))

orSolverType = []
for args_solver in args.or_solver:
	if args_solver != "none": orSolverType.append(next(s for s in list(OrSolvers) if s.value == args_solver))

cpSolverType = [CpSolvers.CPSat] if args.cp_solver else []

gurobiSolverType = []
# gurobiSolverType = [GurobiSolvers.GurobiSolver] if args.gurobi_solver else []

# dump_file = args.dump_file

logging.basicConfig(stream=stdout, level=getattr(logging, args.loglevel))
timeout = args.timeout

# endregion

if not os.path.isfile(inputFile):
	logging.error("Input file {} does not exist".format(inputFile))
	exit()

logging.info("Parsing the file {}".format(inputFile))
with open(inputFile) as file:
	jsonData = json.load(file)

dcnModels = [DcnModel1,DcnModel2]
dcnModel = dcnModels[jsonData["version"] - 1]()
dcnModel.ReadInputFile(jsonData)

startTime = time()

result = Optimize(dcnModel, getModel=True)
	
if result.result == SolverResultType.TIMEOUT:
	print("TIMEOUT")
elif result.result == SolverResultType.SAT:
	logging.info("Result provided by: {}".format(result.solverType))
	print("SAT")
	print("OPTIMUM: {:d}".format(dcnModel.GetObjectiveValue(result.model)))
	logging.info("elapsed time = {:f}".format(time() - startTime))
	if bool_get_scheduling:
		dcnModel.DisplayModel(result.model)
elif result.result == SolverResultType.UNSAT:
	logging.info("Result provided by: {}".format(result.solverType))
	print("UNSAT")
	logging.info("elapsed time = {:f}".format(time() - startTime))
else:
	print("ERROR: no solver provided a result and timed out")

print("ELAPSED TIME = {:f}".format(time() - startTime))

logging.shutdown()
