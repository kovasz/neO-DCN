# -*- coding: utf-8 -*-
from enum import Enum

from solvers.card_enc_type import Relations, RelationOps

SAT = True
UNSAT = False

class SolverResultType(Enum):
	NONE = 0
	UNSAT = 1
	SAT = 2
	TIMEOUT = 3

class SolverResult():
	def __init__(self, solverType = None, isSAT = False, isTIMEOUT = False, model = None):
		self.solverType = solverType
		self.result = SolverResultType.SAT if isSAT else SolverResultType.UNSAT
		if isTIMEOUT: self.result = SolverResultType.TIMEOUT
		# self.isSAT = isSAT
		self.model = model

class Constraint():
	def __init__(self, lits, weights = None, relation = Relations.GreaterOrEqual, bound = 1, boolLit = None):
		"""Instatiate a pseudo-Boolean constraint

		Parameters:

		lits -- literals on the LHS of the constraint

		weights -- weights assigned to literals, respectively

		relation -- relational operator
		
		bound -- bound on the RHS of the constraint

		boolLit -- Boolean literal that implies the constraint (undefined by default)
		boolLit =>  lits*weights relation bound
		"""

		assert(lits is not None)
		self.lits = lits

		assert(weights is None or (len(weights) == len(lits) and all(w >= 0 for w in weights)))
		self.weights = weights

		self.relation = relation
		
		assert(bound >= 0)
		self.bound = bound
		self.boolLit = boolLit

	def __str__(self):
		return "{}{} {} {:d}{}".format(
			self.lits,
			" * {}".format(self.weights) if self.weights is not None else "",
			RelationOps[self.relation],
			self.bound,
			"\t <=> {:d}".format(self.boolLit) if self.boolLit else ""
		)

class Solver(object):
	def generateVars(self, numVars):
		"""Generate certain number of new Boolean vars

		Parameters:

		numVars -- number of new vars

		Returns: list of new variables
		"""

		raise NotImplementedError("Please Implement this method")

	def addClause(self, lits):
		"""Add clause to the solver

		Parameter:

		lits -- literals of the clause
		"""

		raise NotImplementedError("Please Implement this method")

	def addConstraint(self, constraint):
		"""Add constraint to the solver

		Parameters:

		constraint -- constraint to add
		"""

		raise NotImplementedError("Please Implement this method")
	
	def minimize(self, lits, weights = None):
		"""Add a linear expression as an objective function to minimize

		Parameters:

		lits -- literals of the linear expression

		weights -- weights assigned to literals, respectively
		"""

		raise NotImplementedError("Please Implement this method")

	def solve(self):
		"""Start the solving process

		Returns: True iff satisfiable
		"""

		raise NotImplementedError("Please Implement this method")

	def get_model(self, lit):
		"""Get the satisfying model for literals

		Parameters:

		lit -- a literal, or a list/tuple/dictionary of literals

		Returns: assignments to literals in the same structure
		"""

		if not lit:
			return None
		elif isinstance(lit, list):
			return [self.get_model(l) for l in lit]
		elif isinstance(lit, tuple):
			return tuple(self.get_model(l) for l in lit)
		elif isinstance(lit, dict):
			return {k : self.get_model(l) for k, l in lit.items() }
		else:
			raise NotImplementedError(f"Please, implement this method for type {type(lit)}")
