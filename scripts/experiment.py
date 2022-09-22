import subprocess
from parse import parse, search
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
		outputFile.write("file;res;opt;time;mem\n")

	for i in range(len(resultFileNames)):
		resultFile = open(resultFileNames[i], "r")

		cntSolved = cntTimeout = sumTime = sumMem = 0

		for line in resultFile:
			fileNameResult = parse("INFO:root:Parsing the file {}", line)
			if fileNameResult:
				fileName = fileNameResult[0]
				isTimeout = False
			else:
				if parse("SAT", line):
					result = "sat"
					cntSolved += 1
				elif parse("UNSAT", line):
					result = "unsat"
					cntSolved += 1
					optimum = ""
				elif parse("TIMEOUT", line):
					cntTimeout += 1
					sumTime += TIMEOUT
					isTimeout = True
				else:
					optimumResult = parse("OPTIMUM: {:d}", line)
					if optimumResult:
						optimum = optimumResult[0]
						# cntSolved += 1
					else:
						memResult = search("{:f} MiB", line)
						if memResult:
							mem = memResult[0]
							sumMem += mem
							if outputFile:
								if isTimeout:
									outputFile.write("{};;;{:f};{:f}\n".format(fileName, TIMEOUT, mem))
								else:
									outputFile.write("{};{};{};{:f};{:f}\n".format(fileName, result, optimum, runtime, mem))
						elif not isTimeout:
							runtimeResult = parse("ELAPSED TIME = {:f}", line)
							if runtimeResult:
								runtime = runtimeResult[0]
								sumTime += runtime

		resultFile.close()

		print("{}: #solved = {}, #timeout = {}, #avgtime = {}, #avgmem = {}".format(resultFileNames[i], cntSolved, cntTimeout, sumTime / (cntSolved + cntTimeout), sumMem / (cntSolved + cntTimeout)))

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
		# RunCMD("python3.7 ../neO.py {} {} --log INFO --timeout {:d} >> {}".format(inputFile, solverOption, TIMEOUT, outFileName))
		RunCMD("mprof run -C -T 0.5 python3.7 ../neO.py {} {} --log INFO --timeout {:d} >> {}".format(inputFile, solverOption, TIMEOUT, outFileName))
		RunCMD("mprof peak >> {}".format(outFileName))

def MemProf(path, solverOption, outFileName, outCsvFileName):
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
		RunCMD("echo 'File {}' >> {}".format(inputFile, outFileName))
		RunCMD("mprof run -C python3.7 ../neO.py {} {} --timeout {:d}".format(inputFile, solverOption, TIMEOUT))
		RunCMD("mprof peak >> {}".format(outFileName))
		# RunCMD("mprof peak | sed -r 's/.*\s([0-9]+\.[0-9]+) MiB/\1/' >> {}".format(outFileName))

	outCsvFile = open(outCsvFileName, "w")
	outCsvFile.write("file;mem\n")
	resultFile = open(outFileName, "r")

	for line in resultFile:
		fileNameResult = parse("File {}", line)
		if fileNameResult:
			fileName = fileNameResult[0]
		else:
			memResult = search("{:f} MiB", line)
			if memResult:
				mem = memResult[0]
				outCsvFile.write("{};{:f}\n".format(fileName, mem))

	resultFile.close()
	outCsvFile.close()



### MODEL 1

# Solve("../benchmarks/electronics2021/", "--or-solver gurobi", "out/gurobi.out")
# ParseResult(["out/gurobi.out"], "out/gurobi.csv")

# Solve("../benchmarks/electronics2021/", "--or-solver cbc", "out/cbc.out")
# ParseResult(["out/cbc.out"], "out/cbc.csv")

# Solve("../benchmarks/electronics2021/", "--or-solver scip", "out/scip.out")
# ParseResult(["out/scip.out"], "out/scip.csv")

Solve("../benchmarks/electronics2021/", "--cp-solver", "out/cp-sat.out")
ParseResult(["out/cp-sat.out"], "out/cp-sat.csv")

# RunCMD("systemctl poweroff")
