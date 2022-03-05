import subprocess
from parse import parse
from pathlib import Path
import random as rnd
import os
import glob

def RunCMD(cmd):
	subprocess.call(cmd, shell = True)


TIMEOUT = 1200

def ParseResult(resultFileNames, outputFileName = None):
	outputFile = None
	if outputFileName is not None:
		outputFile = open(outputFileName, "w")
		outputFile.write("file;res;opt;time\n")

	for i in range(len(resultFileNames)):
		resultFile = open(resultFileNames[i], "r")

		cntSolved = cntTimeout = sumTime = 0

		for line in resultFile:
			fileNameResult = parse("INFO:root:Parsing the file {}", line)
			if fileNameResult:
				fileName = fileNameResult[0]
			else:
				if parse("SAT", line):
					result = "sat"
					cntSolved += 1
				elif parse("UNSAT", line):
					result = "unsat"
					cntSolved += 1
					optimum = ""
				elif parse("TIMEOUT", line):
					# optimum = 0
					cntTimeout += 1
					sumTime += TIMEOUT
					if outputFile:
						outputFile.write("{};{};-1;{:f}\n".format(fileName, result, TIMEOUT))
					continue

				optimumResult = parse("OPTIMUM: {:d}", line)
				if optimumResult:
					optimum = optimumResult[0]
					# cntSolved += 1
				else:
					runtime = parse("ELAPSED TIME = {:f}", line)
					if runtime:
						sumTime += runtime[0]
						if outputFile:
							outputFile.write("{};{};{};{:f}\n".format(fileName, result, optimum, runtime[0]))

		resultFile.close()

		print("{}: #solved = {}, #avgtime = {}".format(resultFileNames[i], cntSolved, sumTime / (cntSolved + cntTimeout)))

	if outputFile:
		outputFile.close()

def Solve(path, solverOption, outFileName):
	if not os.path.exists(path):
		print("Input path {} does not exist".format(path))
		exit()
	inputFiles = []
	if os.path.isdir(path):
		for file in glob.glob("{}/*.dcn".format(path)):
			inputFiles.append(file)
	else:
		inputFiles.append(path)
	inputFiles.sort()

	Path(outFileName).touch()
	for inputFile in inputFiles:
		RunCMD("python3.7 ../neO.py {} {} --log INFO --timeout {:d} >> {}".format(inputFile, solverOption, TIMEOUT, outFileName))



### MODEL 1

Solve("../benchmarks/electronics2021/", "--or-solver gurobi", "out/gurobi.out")
ParseResult(["out/gurobi.out"], "out/gurobi.csv")

# Solve("../benchmarks/electronics2021/", "--cp-solver", "out/cp-sat.out")
# ParseResult(["out/cp-sat.out"], "out/cp-sat.csv")
