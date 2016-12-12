# In this example, we have a sum of two weighted normal distributions with different parameters. We have a total of 6 parameters.
import numpy as np
import scipy.stats
from matplotlib.pyplot import *
from MCMC import *

# Create MCMC parameters
parameters = {"mu1": Parameter(name="mu1", initialValue=2.3, minValue=-3, maxValue=3, stddev=0.1, fixed=False),
				"sigma1": Parameter(name="sigma1", initialValue=2, minValue=0.2, maxValue=3, stddev=0.1, fixed=False),
				"factor1": Parameter(name="factor1", initialValue=1.0, minValue=0.0, maxValue=2.0, stddev=0.1, fixed=False),
				"mu2": Parameter(name="mu2", initialValue=2.3, minValue=-3, maxValue=3, stddev=0.1, fixed=False),
				"sigma2": Parameter(name="sigma2", initialValue=2, minValue=0.2, maxValue=3, stddev=0.1, fixed=False),
				"factor2": Parameter(name="factor2", initialValue=1.0, minValue=0.0, maxValue=2.0, stddev=0.1, fixed=False)}

# Create random gaussian distributed numbers
mu1_real = 0.1
sigma1_real = 0.9
factor1_real = 1.5

mu2_real = 0.7
sigma2_real = 0.3
factor2_real = 0.9
x = np.random.uniform(-3,3,int(1e3))
y = factor1_real*scipy.stats.norm.pdf(x, loc=mu1_real, scale=sigma1_real) + factor2_real*scipy.stats.norm.pdf(x, loc=mu2_real, scale=sigma2_real)

# Function calculating the chi squared given the model
def chiSquaredCalculator(parameters):
	chiSquared = 0
	y_model = parameters["factor1"].value*scipy.stats.norm.pdf(x, loc=parameters["mu1"].value, scale=parameters["sigma1"].value) + parameters["factor2"].value*scipy.stats.norm.pdf(x, loc=parameters["mu2"].value, scale=parameters["sigma2"].value)
	chiSquared = sum( (y_model - y)**2 / y) / len(x) # TODO: if any y-values are zero, we get troubles
	
	return chiSquared

# Create MCMC object
mcmc = MCMC(parameters=parameters, chiSquaredCalculator = chiSquaredCalculator, temperature=1e-3, verbose = False)
# Do MCMC steps
mcmc.stepMetropolisHastings(numberOfSteps = 1e6)
# Save to file if we want to
mcmc.saveParameters()

# Now do some plotting of the results
if True:
	figure()
	hold('on')
	plot(mcmc.parameters["mu1"].values, color="b", label="$\mu_1$")
	plot([0, mcmc.acceptedSteps], [mu1_real, mu1_real], color="b", label="$\mu_1$ real", linewidth=2)

	plot(mcmc.parameters["mu2"].values, color="g", label="$\mu_2$")
	plot([0, mcmc.acceptedSteps], [mu2_real, mu2_real], color="g", label="$\mu_2$ real", linewidth=2)

	plot(mcmc.parameters["sigma1"].values, color="r", label="$\sigma_1$")
	plot([0, mcmc.acceptedSteps], [sigma1_real, sigma1_real], color="r", label="$\sigma_1$ real", linewidth=2)

	plot(mcmc.parameters["sigma2"].values, color="c", label="$\sigma_2$")
	plot([0, mcmc.acceptedSteps], [sigma2_real, sigma2_real], color="c", label="$\sigma_2$ real", linewidth=2)

	plot(mcmc.parameters["factor1"].values, color="m", label="factor1")
	plot([0, mcmc.acceptedSteps], [factor1_real, factor1_real], color="m", label="factor1 real", linewidth=2)

	plot(mcmc.parameters["factor2"].values, color="y", label="factor2")
	plot([0, mcmc.acceptedSteps], [factor2_real, factor2_real], color="y", label="factor2 real", linewidth=2)
	xlabel('#MC cycles')
	ylabel('Parameter value')
	legend()

figure()
mcmc.plotAllCorrelations()
figure()
mcmc.plotAllParameters(start=int(mcmc.acceptedSteps*0.5))

show()