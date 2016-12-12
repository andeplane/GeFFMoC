import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from matplotlib.colors import LogNorm
class Parameter:
	def __init__(self, name, initialValue, minValue, maxValue, stddev, fixed):
		self.minValue = minValue
		self.maxValue = maxValue
		self.stddev = stddev
		self.name = name
		self.value = initialValue
		self.oldValue = self.value
		self.fixed = fixed
		self.values = [self.value]

	def insertValue(self, line):
		replaceString = "@"+self.name.upper()
		line = line.replace(replaceString, str(self.value))
		return line

	def randomWalk(self):
		if self.fixed: return
		self.oldValue = self.value
		deltaValue = np.random.normal(0, self.stddev)
		self.value += deltaValue
		if self.value > self.maxValue: self.value = self.maxValue
		if self.value < self.minValue: self.value = self.minValue
		
	def reject(self):
		self.value = self.oldValue

	def accept(self):
		self.values.append(self.value)

	def plotHistogram(self, bins = 100, start = 0):
		ax = plt.gca()
		plt.hist(self.values[start:-1], bins=bins, normed=True)
		mu, sigma = scipy.stats.norm.fit(self.values)
		xMin = min(self.values)
		if xMin < 0:
			xMin *= 1.2
		else: 
			xMin *= 0.9
		xMax = max(self.values)
		if xMax < 0:
			xMax *= 0.9
		else: 
			xMax *= 1.2
		x = np.linspace(xMin, xMax, 1e3)
		y = scipy.stats.norm.pdf(x, loc=mu, scale=sigma)
		plt.hold('on')
		plt.plot(x,y)
		plt.title(self.name)
		textstr = '$\mu=%.2f$\n$\sigma=%.2f$'%(mu, sigma)
		props = dict(boxstyle='round', facecolor='white', alpha=0.5)
		ax.text(0.85, 0.85, textstr, transform=ax.transAxes, fontsize=14,
	        verticalalignment='top', bbox=props)

	def save(self):
		fileName = "%s.txt" % self.name
		np.savetxt(fileName, np.array(self.values))


class MCMC:
	def __init__(self, parameters, chiSquaredCalculator, templateFileName = None, inputFileName = None, verbose = False, temperature = 1.0):
		self.parameters = parameters
		self.chiSquaredCalculator = chiSquaredCalculator
		self.chiSquared = float("Inf")
		self.oldChiSquared = float("Inf")
		self.temperature = temperature
		self.steps = 0
		self.acceptedSteps = 0
		self.templateFileName = templateFileName
		self.inputFileName = inputFileName
		self.verbose = verbose

	def walkParams(self):
		for parameterKey in self.parameters:
			self.parameters[parameterKey].randomWalk()
			if self.verbose:
				print "New value for ", parameterKey, ": ", self.parameters[parameterKey].value

	def writeInputFiles(self, templateFileName = None, inputFileName = None):
		# If we're not using input files, just skip this part
		if self.templateFileName is None and self.inputFileName is None:
			return

		# We use this function recursively. If input parameters to this function are set,
		# they are strings containing the filenames.
		if templateFileName is not None and inputFileName is not None:
			try:
				with open(templateFileName, 'r') as templateFile:
					with open(inputFileName, 'w') as inputFile:
						contents = templateFile.readlines()
						for line in contents:
							for parameterKey in self.parameters:
								line = self.parameters[parameterKey].insertValue(line)
							inputFile.write(line+"\n")
			except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
				exit("Error opening file...")
			return

		# If we have multiple filenames in a list, loop through each pair of filenames 
		if isinstance(self.templateFileName, list) and isinstance(self.inputFileName, list):
			if len(self.templateFileName) != len(self.inputFileName):
				exit("Error, length of lists templateFileName and inputeFileName does not mach, aborting.")

			for i in range(len(self.templateFileName)):
				self.writeInputFiles(self.templateFileName[i], self.inputFileName[i])
		else:
			self.writeInputFiles(self.templateFileName, self.inputFileName)
		

	def accept(self):
		self.acceptedSteps += 1
		for parameterKey in self.parameters:
			self.parameters[parameterKey].accept()

	def reject(self):
		self.chiSquared = self.oldChiSquared
		for parameterKey in self.parameters:
			self.parameters[parameterKey].reject()
	
	def acceptanceRatio(self):
		return self.acceptedSteps / float(self.steps)

	def saveParameters(self):
		for parameterKey in self.parameters:
			self.parameters[parameterKey].save()

	def plotCorrelation(self, parameter1, parameter2, bins = 40, logarithmic = False, colorbar = True):
		if logarithmic:
			plt.hist2d(parameter1.values, parameter2.values, bins = bins, norm=LogNorm())
		else: 
			plt.hist2d(parameter1.values, parameter2.values, bins = bins)
		if colorbar:
			plt.colorbar()
	
	def plotAllParameters(self, bins = 100, start = 0):
		numFiguresPerDimension = np.ceil(np.sqrt(self.numberOfVaryingParameters()))
		i = 0
		for parameterKey in self.parameters:
			if self.parameters[parameterKey].fixed: continue
			i += 1
			plt.subplot(numFiguresPerDimension, numFiguresPerDimension, i)
			self.parameters[parameterKey].plotHistogram(bins=bins, start = start)

	def numberOfVaryingParameters(self):
		return sum([int(not self.parameters[key].fixed) for key in self.parameters])

	def plotAllCorrelations(self):
		numberOfVaryingParameters = self.numberOfVaryingParameters()

		keys = self.parameters.keys()
		for i in range(len(keys)):
			for j in range(i+1, len(keys),1):
				figNumber = numberOfVaryingParameters*numberOfVaryingParameters - (i*len(keys) + j)
				plt.subplot(numberOfVaryingParameters, numberOfVaryingParameters, figNumber)
				self.plotCorrelation(self.parameters[keys[i]], self.parameters[keys[j]], colorbar = False)
				plt.title(self.parameters[keys[i]].name+" and "+self.parameters[keys[j]].name)
				plt.axis('off')
				
	def stepMetropolisHastings(self, numberOfSteps = 1):
		numberOfSteps = int(numberOfSteps)
		for i in range(numberOfSteps):
			self.steps += 1
			self.walkParams()
			self.writeInputFiles()
			self.oldChiSquared = self.chiSquared
			self.chiSquared = self.chiSquaredCalculator(parameters = self.parameters)
			deltaChiSquared = self.chiSquared - self.oldChiSquared
			if self.verbose:
				print "Old chisq: ", self.oldChiSquared, " new chisq: ", self.chiSquared, " deltaChisq: ", deltaChiSquared
			if np.random.uniform(0,1) < np.exp(-deltaChiSquared/self.temperature):
				if self.verbose: print "Accepted"
				self.accept()
			else:
				if self.verbose: print "Rejected"
				self.reject()
			# 
			if i % 100 == 0:
				print self.steps, "/", numberOfSteps, " steps with acceptance ratio ", self.acceptanceRatio()

