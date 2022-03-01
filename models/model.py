# -*- coding: utf-8 -*-

import logging

class DcnModel(object):
	def ReadInputFile(self, filename):
		"""Read the input file with DCN data

		Parameters:

		filename -- name of the input file
		"""

		raise NotImplementedError("Please Implement this method")

	def EncodeDcnConstraints(self, solver):
		"""Encode all the WSN constraints

		Parameters:

		solver -- solver to encode the constraints for

		Returns: list of scheduling vars
		"""

		raise NotImplementedError("Please Implement this method")

	def GetObjectiveValue(self, model):
		"""Returns the objective value

		Parameters:

		model -- optimal model
		"""

		raise NotImplementedError("Please Implement this method")
	def DisplayModel(self, model):
		"""Display the model

		Parameters:

		model -- optimal model
		"""

		raise NotImplementedError("Please Implement this method")