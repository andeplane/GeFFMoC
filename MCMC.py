import numpy

class Parameter:
	def __init__(self, name, initialValue, minValue, maxValue, stddev):
		self.min = minValue
		self.max = maxValue
		self.stddev = stddev
		self.name = name
		self.value = initialValue
		self.oldValue = value
		self.values = [self.value]

	def insertValue(self, line):
		replaceString = "__"+self.name.toUpper()+"__"
		line = line.replace(replaceString, str(self.value))
		return line

	def randomWalk(self):
		oldValue = self.value
		deltaValue = numpy.random.normal(0, stddev, 1)
		self.value += deltaValue

	def reject(self):
		self.value = self.oldValue

	def accept(self):
		self.values.append(self.value)


class MCMC:
	def __init__(self, parameters, calculateChiSquared, templateFileName, inputFileName):
		self.parameters = parameters
		self.calculateChiSquared = calculateChiSquared
		self.chiSquared = inf
		self.oldChiSquared = inf
		self.temperature = 1.0
		self.steps = 0
		self.acceptedSteps = 0
		self.templateFileName = templateFileName
		self.inputFileName = inputFileName

	def walkParams(self):
		for parameter in self.parameters:
			parameter.randomWalk()

	def writeInputFile(self):
		with open(self.templateFileName, 'r') as templateFile:
			with open(self.inputFileName, 'w') as inputFile:
				contents = templateFile.readAll()
				for line in contents:
					for parameter in self.parameters:
						line = parameter.insertValue(line)
						inputFile.write(line+"\n")

	def accept(self):
		self.acceptedSteps += 1

	def reject(self):
		self.chiSquared = self.oldChiSquared

	def stepMetropolisHastings(self):
		self.steps += 1
		self.walkParams()
		self.writeInputFile()
		self.oldChiSquared = self.chiSquared
		self.chiSquared = self.calculateChiSquared()
		deltaChiSquared = self.chiSquared - self.oldChiSquared
		if exp(-deltaChiSquared/self.temperature) < numpy.random.uniform(0,1,1):
			accept()
		else:
			reject()
		












