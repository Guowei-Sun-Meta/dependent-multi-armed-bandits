# Dependent Bandits

this is to pick up the research idea we had during graduate school: a traditional multi-armed bandits problem deals with independet rewards. What if we can introduce dependency?

There are two types of dependencies:
1. Within-arm dependency. What if each sample is not drawn from an iid distribution, what if it is drawn from a time series process such as an ARIMA process where the reward distribution at time t, is dependent on previous rewards at times t-1, .., 0. In the case of rewards being Markovian, then reward at time t is only dependent on rewards realized at time t-1
2. Cross-arm dependnecy. What if arms {a1,...ak} are not independent, what if say a1 and a2 are "closer" than a1 and ak, and the correlation can be modeled via a Gaussian process, where the mean values of rewards for ai,aj can be modeled with correlation determined by a distance function dij?

Under the two types of dependency, how would the optimal policy of reducing regret change? Do some research and evaluate the value of the idea.

