import argparse
import os
import glob
from pathlib import PurePosixPath
from openpyxl import load_workbook
import json

class Model(object):
	@staticmethod
	def generateBenchmark(inputFile, outputDir, numberOfFlows):
		raise NotImplementedError()

class Model1(Model):
	@staticmethod
	def __generateLinks():
		return [
		{
			"source": 1,
			"destination": 17
		},
		{
			"source": 2,
			"destination": 17
		},
		{
			"source": 3,
			"destination": 18
		},
		{
			"source": 4,
			"destination": 18
		},
		{
			"source": 5,
			"destination": 19
		},
		{
			"source": 6,
			"destination": 19
		},
		{
			"source": 7,
			"destination": 20
		},
		{
			"source": 8,
			"destination": 20
		},
		{
			"source": 9,
			"destination": 21
		},
		{
			"source": 10,
			"destination": 21
		},
		{
			"source": 11,
			"destination": 22
		},
		{
			"source": 12,
			"destination": 22
		},
		{
			"source": 13,
			"destination": 23
		},
		{
			"source": 14,
			"destination": 23
		},
		{
			"source": 15,
			"destination": 24
		},
		{
			"source": 16,
			"destination": 24
		},
		{
			"source": 17,
			"destination": 25
		},
		{
			"source": 17,
			"destination": 26
		},
		{
			"source": 18,
			"destination": 25
		},
		{
			"source": 18,
			"destination": 26
		},
		{
			"source": 19,
			"destination": 27
		},
		{
			"source": 19,
			"destination": 28
		},
		{
			"source": 20,
			"destination": 27
		},
		{
			"source": 20,
			"destination": 28
		},
		{
			"source": 21,
			"destination": 29
		},
		{
			"source": 21,
			"destination": 30
		},
		{
			"source": 22,
			"destination": 29
		},
		{
			"source": 22,
			"destination": 30
		},
		{
			"source": 23,
			"destination": 31
		},
		{
			"source": 23,
			"destination": 32
		},
		{
			"source": 24,
			"destination": 31
		},
		{
			"source": 24,
			"destination": 32
		},
		{
			"source": 25,
			"destination": 33
		},
		{
			"source": 25,
			"destination": 34
		},
		{
			"source": 26,
			"destination": 35
		},
		{
			"source": 26,
			"destination": 36
		},
		{
			"source": 27,
			"destination": 33
		},
		{
			"source": 27,
			"destination": 34
		},
		{
			"source": 28,
			"destination": 35
		},
		{
			"source": 28,
			"destination": 36
		},
		{
			"source": 29,
			"destination": 33
		},
		{
			"source": 29,
			"destination": 34
		},
		{
			"source": 30,
			"destination": 35
		},
		{
			"source": 30,
			"destination": 36
		},
		{
			"source": 31,
			"destination": 33
		},
		{
			"source": 31,
			"destination": 34
		},
		{
			"source": 32,
			"destination": 35
		},
		{
			"source": 33,
			"destination": 36
		}
			]

	@staticmethod
	def __generateFlows(inputFile):
		sheet = load_workbook(inputFile).active

		flows = []
		
		i = 2
		while sheet["B"][i].value:
			flows.append({
				"source": sheet["B"][i].value,
				"destination": sheet["C"][i].value,
				"packet rate": sheet["D"][i].value
			})
			i += 1
		
		return flows

	@staticmethod
	def generateBenchmark(inputFile, outputDir):
		content = {
			"version": 1,
			"number of switches": 36,
			"links": Model1.__generateLinks(),
			"flows": Model1.__generateFlows(inputFile),
		}

		with open("{}/{}.dcn".format(outDir, PurePosixPath(inputFile).stem), "w") as outFile:
			outFile.write(json.dumps(content, indent = 4))
			outFile.close()



parser = argparse.ArgumentParser("Convert an Excel file (used as input for LINGO) to a JSON file (as input for neO)")

parser.add_argument("path", help="path to XLSX file(s)")

# parser.add_argument("-m1", "--model 1",
#                     action="store_true", dest="model_1",
#                     help="generate model 1 network")
args = parser.parse_args()

# Checking and collecting the input files
if not os.path.exists(args.path):
	print("Input path {} does not exist".format(args.path))
	exit()
inputFiles = []
if os.path.isdir(args.path):
	for file in glob.glob("{}/*.xlsx".format(args.path)):
		inputFiles.append(file)
else:
	inputFiles.append(args.path)

# Creating and cleaning out directory
outDir = "./out"
if not os.path.exists(outDir):
	os.makedirs(outDir)

for file in inputFiles:
		Model1.generateBenchmark(file, outDir)

print("Files converted!")