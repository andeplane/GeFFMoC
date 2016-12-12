# This example shows how we can use GeFFMoC to find the two parameters in a normal distribution based on data points.
import numpy as np
import scipy.stats
from matplotlib.pyplot import *
from MCMC import *

# Create MCMC parameters
parameters = {"mu": Parameter(name="mu", initialValue=2.3, minValue=-3, maxValue=3, stddev=0.1, fixed=False),
				"sigma": Parameter(name="sigma", initialValue=2, minValue=0.2, maxValue=3, stddev=0.1, fixed=False)}

# Create random gaussian distributed numbers
mu_real = 0.0
sigma_real = 1.0
x = np.random.uniform(-3,3,int(1e3))
y = scipy.stats.norm.pdf(x, loc=mu_real, scale=sigma_real)

# Function calculating the chi squared given the model
def chiSquaredCalculator(parameters):
	chiSquared = 0
	y_model = scipy.stats.norm.pdf(x, loc=parameters["mu"].value, scale=parameters["sigma"].value)
	chiSquared = sum( (y_model - y)**2 / y) / len(x) # TODO: if any y-values are zero, we get troubles
	
	return chiSquared

# Create MCMC object
mcmc = MCMC(parameters=parameters, chiSquaredCalculator = chiSquaredCalculator, temperature=1e-3, verbose = False)
# Do MCMC steps
mcmc.stepMetropolisHastings(numberOfSteps = 1e4)
# Save to file if we want to
mcmc.saveParameters()

# Now plot each parameter as as a function of mc cycles
figure()
hold('on')
plot(mcmc.parameters["mu"].values, color="blue", label="$\mu$")
plot(mcmc.parameters["sigma"].values, color="red", label="$\sigma$")
plot([0, mcmc.acceptedSteps], [mu_real, mu_real], color="blue", label="$\mu$ real", linewidth=2)
plot([0, mcmc.acceptedSteps], [sigma_real, sigma_real], color="red", label="$\sigma$ real", linewidth=2)
xlabel('#MC cycles')
ylabel('Parameter value')
legend()

# Correlation between the two parameters
figure()
mcmc.plotCorrelation(parameter1 = parameters["mu"], parameter2 = parameters["sigma"], bins=50, logarithmic = True)
# Correlation between the two parameters
figure()
mcmc.plotAllParameters()
show()
