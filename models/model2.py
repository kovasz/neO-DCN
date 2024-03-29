# -*- coding: utf-8 -*-

from math import pow, sqrt, ceil
import logging

from solvers.card_enc_type import Relations
from solvers.solver import Constraint

from models.model import DcnModel

class Link:
	def __init__(self, source, destination):
		self.source = source
		self.destination = destination
		self.load = 0

	def __str__(self):
		return "({:d},{:d}): load = {:d}".format(self.source, self.destination, self.load)

class Flow:
	def __init__(self, source, destination, packetRate):
		self.source = source
		self.destination = destination
		self.packetRate = packetRate

	def __str__(self):
		return "({:d},{:d}): packetRate = {:d}".format(self.source, self.destination, self.packetRate)

class DcnModel2(DcnModel):
	def __init__(self):
		super().__init__()
		self.numberOfServers = 0
		self.numberOfSwitches = 0
		self.links = None
		self.flows = None

	def ReadInputFile(self, json):
		self.numberOfServers = json["number of servers"]
		self.numberOfSwitches = json["number of switches"]

		self.links = []
		for f in json["links"]:
			self.links.append(Link(f["source"], f["destination"]))
			self.links.append(Link(f["destination"], f["source"]))

		self.flows = []
		for f in json["flows"]:
			self.flows.append(Flow(f["source"], f["destination"], f["packet rate"]))

		if self.numberOfServers == 0:
			raise Exception("No servers specified")
		if self.numberOfSwitches == 0:
			raise Exception("No switches specified")
		if len(self.links) == 0:
			raise Exception("No links specified")
		if len(self.flows) == 0:
			raise Exception("No flows specified")

	def EncodeDcnConstraints(self, solver):
		# generate vars

#		switchVars = solver.generateVars(self.numberOfSwitches + self.numberOfServers + 1)
		switchVars = {s : solver.generateVars(1)[0] for s in range(1, self.numberOfServers + self.numberOfSwitches + 1)}
		linkVars = {}
		flowVars = {}
		for l in self.links:
			linkVars[(l.source, l.destination)] = solver.generateVars(1)[0]
			flowVars[(l.source, l.destination)] = solver.generateVars(len(self.flows))
		
		# MIN = @SUM(EDGES: L);
		solver.minimize(list(linkVars.values()) + [v for k,v in switchVars.items() if k > self.numberOfServers])

		# @FOR(FLOWS(f):@FOR(SWITCHES(i):@FOR(SWITCHES(j): 
		# 	FR(f,i,j) <= L(i,j)
		for l in self.links:
			for fIndex in range(len(self.flows)):
				solver.addClause([-flowVars[(l.source, l.destination)][fIndex], linkVars[(l.source, l.destination)]])
		
		# @FOR(FLOWS(f):
		# 	@SUM(SWITCHES(i): FR(f,SOURCE(f),i))=1
		# @FOR(FLOWS(f):
		# 	@SUM(SWITCHES(i): FR(f,i,DEST(f)))=1
		### IS THIS REALLY NECESSARY AND/OR SOUND?
		for fIndex, f in enumerate(self.flows):
			solver.addClause(
				[flowVars[(l.source, l.destination)][fIndex]
				for l in self.links if l.source == f.source])
			solver.addClause(
				[flowVars[(l.source, l.destination)][fIndex]
				for l in self.links if l.destination == f.destination])
		
		# @FOR(FLOWS(f): @FOR(SWITCHES(i):
		#  @FOR(SWITCHES(j):
		# 		FR(f,i,j)+FR(f,j,i) <= 1
		for l in self.links:
			if l.source > l.destination: continue
			for fIndex in range(len(self.flows)):
				solver.addClause([-flowVars[(l.source, l.destination)][fIndex], -flowVars[(l.destination, l.source)][fIndex]])

		# @FOR(FLOWS(f): @FOR(SWITCHES(i) | i #ne# SOURCE(f) #AND# i #ne# DEST(f):
		# 	@SUM(SWITCHES(j): FR(f,j,i)) = @SUM(SWITCHES(k): FR(f,i,k))
		for fIndex, f in enumerate(self.flows):
			for l1 in self.links:
				if l1.destination != f.source and l1.destination != f.destination:
					solver.addClause([-flowVars[(l1.source, l1.destination)][fIndex]] +
						[flowVars[(l2.source, l2.destination)][fIndex]
						for l2 in self.links if l1.destination == l2.source])
				# this might be unnecessary due to undirected links
				if l1.source != f.source and l1.source != f.destination:
					solver.addClause([-flowVars[(l1.source, l1.destination)][fIndex]] +
						[flowVars[(l2.source, l2.destination)][fIndex]
						for l2 in self.links if l1.source == l2.destination])

		# @FOR(SWITCHES(i): @FOR(SWITCHES(j): 
		# 	U(i,j) = @SUM(FLOWS(f): FR(f,i,j)*LAMBDA(f) + FR(f,j,i)*LAMBDA(f))
		# ));
		# @FOR(SWITCHES(i): @FOR(SWITCHES(j): 
		# 	U(i,j) <= 1000 - LOAD(i,j)
		# ));
		for l in self.links:
			if l.source > l.destination: continue

			lits = []
			weights = []
			for fIndex, f in enumerate(self.flows):
				# lits.append(flowVars[(l.source, l.destination)][fIndex])
				# weights.append(f.packetRate)
				lits.extend([flowVars[(l.source, l.destination)][fIndex], flowVars[(l.destination, l.source)][fIndex]])
				weights.extend([f.packetRate, f.packetRate])
			solver.addConstraint(Constraint(
						lits = lits,
						weights = weights,
						relation = Relations.LessOrEqual,
						bound = 1000 - l.load
					))

		# @FOR(SWITCHES(i): @FOR(SWITCHES(j):
		# 		LOAD(i,j) / 1000 <= L(i,j)
		# ));
		### WHAT TO DO WITH THIS?

# new constraint: "Graph connection constraint"
		for l in self.links:
			solver.addClause([switchVars[l.source], -linkVars[(l.source, l.destination)]])
			solver.addClause([switchVars[l.destination], -linkVars[(l.source, l.destination)]])

#		outputVars = [[switchVars],[]]
		outputVars = {"switches": [], "links": []}
		outputVars["switches"] = [ v for k,v in switchVars.items() if k > self.numberOfServers ]
		for l in self.links:
#			outputVars[1].append([ linkVars[(l.source, l.destination)], flowVars[(l.source, l.destination)] ])
			outputVars["links"].append( (linkVars[(l.source, l.destination)] , flowVars[(l.source, l.destination)]) )
		return outputVars

	def GetObjectiveValue(self, model):
#		return sum(model[1][i][0] for i in range(len(self.links))) + sum()
		return sum(s[0] for s in model["links"]) + sum(model["switches"])

	def DisplayModel(self, model):
		for sIndex, s in enumerate(model["switches"]):
			# print("{} {:d}: \t{:d}".format("Server" if sIndex < self.numberOfServers else "Switch", sIndex + 1, s))
			print("Switch {:d}: \t{:d}".format(self.numberOfServers + 1 + sIndex, s))

		for lIndex, l in enumerate(self.links):
			print("Link ({:d},{:d}):\t{:d}".format(l.source, l.destination, model["links"][lIndex][0]))

		for fIndex, f in enumerate(self.flows):
			print("Flow ({:d},{:d}):".format(f.source, f.destination), end = " ")
			for lIndex, l in enumerate(self.links):
				l_val, flows = model["links"][lIndex]
				if l_val == 1 and flows[fIndex] == 1:
					print("({:d},{:d})".format(l.source, l.destination), end = " ")
			print()
