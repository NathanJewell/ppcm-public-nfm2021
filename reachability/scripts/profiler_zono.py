from matplotlib import pyplot as plt
import numpy as np
from nl_dynamics import F1Dynamics
from functools import partial
import math
import time
from timeit import Timer
from run_f1zono import run_quickzono
import pstats


#TODO graph timing only for zono projections

linear = lambda mini, maxi, frac : mini + (maxi - mini) * frac

numDataTrials = 4

#dt config
dt_Min = .01
dt_Max = .15
dt_numSteps = 5
dt_StepFunc = linear
dt_Steps = [dt_StepFunc(dt_Min, dt_Max, step/(dt_numSteps)) for step in range(dt_numSteps)]
print("DT steps are:")
print(dt_Steps)

#total time config
ttime_Min = .5
ttime_Max = 1
ttime_numSteps = 2
ttime_StepFunc = linear
ttime_Steps = [ttime_StepFunc(ttime_Min, ttime_Max, step/(ttime_numSteps)) for step in range(ttime_numSteps)]
print("Total Time Steps are")
print(ttime_Steps)

#tuple result pairs (ttime, dt, runtime)
def printResult(r):
    print("\033[0;32;40m Run complete with: runtime avg={}\n".format(r[2]))

results = []

maxSimSteps = 50
#testing on dt and total
for totalTime in ttime_Steps:
    print("-----------------------------------")
    print("\033[0;32;40m Running time series with: ttime={}\033[0;37;40m".format(totalTime))
    print("-----------------------------------")
    step_results = []
    for dt in dt_Steps:
        if totalTime / dt < maxSimSteps:
            print("\033[0;32;40m Running model with : ttime={}, dt={}\033[0;37;40m".format(totalTime, dt))
            stamp = "{}{}".format(totalTime, dt).replace('.','d')
            runTimeTrials = []
            print("Trials completed... \n", end='')
            for t in range(numDataTrials):
                print("{}".format(t+1), end=' ')
                runTimeTrials.append(run_quickzono(dt, totalTime, [0, 0, 0], True))

            #with open('profiler/raw/profile_out_{}_{}.txt'.format(dt*1000,totalTime), 'w+') as stream:
                #p = pstats.Stats('profiler/prof/out_tmp.prof', stream=stream)
                #p = p.sort_stats("cumtime").print_stats()
            runTime = np.mean(runTimeTrials)
            result = (totalTime, dt, runTime, int(totalTime / dt))
            printResult(result)
            step_results.append(result)
        else:
            print("\033[2;33;40m SKIPPING model with : ttime={}, dt={}\n".format(totalTime, dt))
    results.append(step_results)

maxRuntime = 0
maxRuntimeRatio = 0
xAxis_padding = .01
yAxis_padding = .1
for ttime_set in results:
    ttime, dt, runtime, steps = zip(*ttime_set)
    maxRuntime = max(max(runtime), maxRuntime)
    maxRuntimeRatio = max(max([r/ttime[0] for r in runtime]), maxRuntimeRatio)

for ttime_set in results:
    ttime, dt, runtime,steps = zip(*ttime_set)
    print("\033[0;37;40m Plotting with ttime={}".format(ttime))
    plt.title("DT Series (T={})".format(ttime[0]))
    plt.ylabel("runtime avg ({} trials)".format(numDataTrials))
    plt.xlabel("dt")
    plt.plot(dt, runtime, '--bo')
    plt.axis([0, dt_Max, 0, maxRuntime])
    plt.savefig("profiler/{}-g.png".format(ttime[0]))
    plt.clf()

#combined dt series vs time
print("\033[0;37;40m Plotting combined".format(ttime))
plt.title("Combined step series by horizon time")
plt.ylabel("runtime avg ({} trials)".format(numDataTrials))
plt.xlabel("steps")
for ttime_set in results:
    ttime, dt, runtime, steps = zip(*ttime_set)
    plt.plot(steps, runtime, marker='o', linestyle='dashed', label="T={}".format(ttime[0]))

plt.axis([
    0,
    maxSimSteps,
    0, 
    maxRuntime + yAxis_padding
])

plt.legend(loc='best')
plt.savefig("profiler/combined-g.png")
plt.clf()

#combined dt series vs runtime/ttime
print("\033[0;37;40m Plotting combined runtime/ttime".format(ttime))
plt.title("Combined dt series by runtime/horizon time")
plt.ylabel("runtime avg / ttime")
plt.xlabel("dt")
for ttime_set in results:
    ttime, dt, runtime,steps = zip(*ttime_set)
    plt.plot(dt, [r/ttime[0] for r in runtime], marker='o', markersize='5', linestyle='dashed', label="T={}".format(ttime[0]))

plt.axis([
    dt_Min - xAxis_padding,
    dt_Max + xAxis_padding, 
    0, 
    maxRuntimeRatio + yAxis_padding
])

plt.legend(loc='best')
plt.savefig("profiler/ratio-g.png")
plt.clf()

print(results)
