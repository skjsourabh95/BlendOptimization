import json
import random

import numpy as np

np.seterr(divide='ignore', invalid='ignore')
from deap import creator, base, tools, algorithms
from scipy.optimize import differential_evolution


def clean_input(inp):
    """replaces the blank values with 0"""
    for tank in inp['tanks']:
        for key, value in tank.items():
            if value == "" or value == " ":
                tank[key] = 0
    for key, value in inp["targetBlend"].items():
        if value == "" or value == " ":
            tank[key] = 0
    return inp


def intermediate_calculation_function(inp, tankVolumes):
    """Given the tank values calculates the necessary intermediate values"""
    for tank, tankVolume in zip(inp['tanks'], tankVolumes):
        tank['specificGravity'] = 141.5 / (tank['API'] + 131.5)
        tank['Mt'] = (tankVolume * (tank['specificGravity'] - 0.00121127225)) / 6.29506768
        tank['costMT'] = tank['Cost'] * 6.29506768 / (tank['specificGravity'] - 0.00121127225)
        tank['Svis'] = max(1.5, tank['Viscosity'])
        tank['Hf'] = tankVolume * np.log(np.log(tank['Svis'] + 0.85))
        tank['specificGravityTotal'] = tankVolume * tank['specificGravity']
        tank['totalCost'] = tankVolume * tank['Cost']
        tank['Smt'] = tank['Mt'] * tank['SulfurPcnt']
        tank['Vmt'] = tank['Mt'] * tank['V']
        tank['Namt'] = tank['Mt'] * tank['Na']
        tank['flashTotal'] = tankVolume * (np.exp((np.log(460 + tank['Flash']) / -0.06)))
        tank['Ashmt'] = tank['Mt'] * tank['WaterPcnt']
        tank['Simt'] = tank['Mt'] * tank['Si']
        tank['Almt'] = tank['Mt'] * tank['AlSi']
        tank['Asphmt'] = tank['Mt'] * tank['AsphPcnt']
        tank['CCRmt'] = tank['Mt'] * tank['MCRTPcnt']

    return inp


def calculate_optimized_blend(inp, tankVolumes):
    """Given the tank values and the intermediate calculations this calulates the optimized blend values"""
    optimized_blend = {}
    optimized_blend['Volume'] = sum(tankVolumes)
    optimized_blend['totalMt'] = sum([item['Mt'] for item in inp['tanks']])
    optimized_blend['specificGravity'] = sum([item['specificGravityTotal'] for item in inp['tanks']]) / \
                                         optimized_blend['Volume']
    optimized_blend['API'] = 141.5 / optimized_blend['specificGravity'] - 131.5
    optimized_blend['Viscosity'] = np.exp(
        np.exp(sum([item['Hf'] for item in inp['tanks']]) / optimized_blend['Volume'])) - 0.8
    optimized_blend['Cost'] = sum([item['totalCost'] for item in inp['tanks']]) / optimized_blend['Volume']
    optimized_blend['SulfurPcnt'] = sum([item['Smt'] for item in inp['tanks']]) / optimized_blend['totalMt']
    optimized_blend['Flash'] = np.exp(
        -0.06 * np.log(sum([item['flashTotal'] for item in inp['tanks']]) / optimized_blend['Volume'])) - 460
    optimized_blend['WaterPcnt'] = sum([item['Ashmt'] for item in inp['tanks']]) / optimized_blend['totalMt']
    optimized_blend['AsphPcnt'] = sum([item['Asphmt'] for item in inp['tanks']]) / optimized_blend['totalMt']
    optimized_blend['AlSi'] = sum([item['Almt'] for item in inp['tanks']]) / optimized_blend['totalMt']
    optimized_blend['Si'] = sum([item['Simt'] for item in inp['tanks']]) / optimized_blend['totalMt']
    optimized_blend['V'] = sum([item['Vmt'] for item in inp['tanks']]) / optimized_blend['totalMt']
    optimized_blend['Na'] = sum([item['Namt'] for item in inp['tanks']]) / optimized_blend['totalMt']
    optimized_blend['MCRTPcnt'] = sum([item['CCRmt'] for item in inp['tanks']]) / optimized_blend['totalMt']
    optimized_blend['Density'] = np.round(141.5 / (131.5 + optimized_blend['API']) * 0.9994, 4) * 1000
    optimized_blend['CCAI'] = optimized_blend['Density'] - 81 - 141 * np.log(
        np.log(optimized_blend['Viscosity'] + 0.85))
    return optimized_blend


def check_constraints(optimized_blend, inp, tankVolumes):
    """This checks whether the given tank volumes passes the required constraints or not"""
    targetBlend = inp['targetBlend']
    assert round(optimized_blend['Na']) <= targetBlend['Na']
    assert round(optimized_blend['V']) <= targetBlend['V']
    assert round(optimized_blend['MCRTPcnt']) <= targetBlend['MCRTPcnt']
    assert round(optimized_blend['Si']) <= targetBlend['Si']
    assert round(optimized_blend['AsphPcnt']) <= targetBlend['AsphPcnt']
    assert round(optimized_blend['AlSi']) <= targetBlend['AlSi']
    assert round(optimized_blend['WaterPcnt']) <= targetBlend['WaterPcnt']
    assert round(optimized_blend['Viscosity']) >= targetBlend['minViscosity']
    assert round(optimized_blend['Viscosity']) <= targetBlend['maxViscosity']
    assert round(optimized_blend['Flash']) >= targetBlend['Flash']
    assert round(optimized_blend['API']) >= targetBlend['API']
    assert round(optimized_blend['SulfurPcnt']) <= targetBlend['SulfurPcnt']
    assert round(optimized_blend['CCAI']) <= targetBlend['CCAI']
    for tank, tankVolume in zip(inp['tanks'], tankVolumes):
        assert tankVolume <= tank['maximumVolume']
        assert tankVolume >= tank['minimumVolume']


def cal_cost(optimized_blend):
    """The cost function that returns the cost which has to be minimized"""
    return optimized_blend["Volume"] * optimized_blend["Cost"] / optimized_blend["totalMt"]


def optimizer_function_de(x, args):
    """Optimizer function for differntial evolution to take tank volumes and return the cost computed"""
    inp = intermediate_calculation_function(args, x)
    optimized_blend = calculate_optimized_blend(inp, x)
    cost = cal_cost(optimized_blend)
    try:
        check_constraints(optimized_blend, inp, x)
        return cost
    except AssertionError:
        return 10 ** 7


def optimizer_function_deap(x, args):
    """Optimizer function for deap to take tank volumes and return the cost computed as a list"""
    inp = intermediate_calculation_function(args, x)
    optimized_blend = calculate_optimized_blend(inp, x)
    cost = cal_cost(optimized_blend)
    try:
        check_constraints(optimized_blend, inp, x)
        return [cost]
    except AssertionError as e:
        return [10 ** 7]


def generate(bounds):
    """creates a search space for the given values within the bound provided"""
    part = creator.Particle(
        random.uniform(bound[0], bound[1]) for bound in bounds)  # generates a random value for the particle
    return part


def deap_calculation(bounds, args):
    """calculates the minimum cost using deap genetic algorithm"""
    # weights = -1.o signifies we want to minimize the value
    creator.create("FitnessMin", base.Fitness, weights=[-1.0])
    # a list is created to represent the particle and take the best of the value seen so far
    creator.create("Particle", list, fitness=creator.FitnessMin, best=None)

    toolbox = base.Toolbox()
    # genearte a particle population space
    toolbox.register("particle", generate, bounds=bounds)
    toolbox.register("population", tools.initRepeat, list, toolbox.particle)
    # perform crossover mating and mutation of the produced children population
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.08)
    # define the evaluation function
    toolbox.register("evaluate", optimizer_function_deap, args=args)
    # Select the best individual among tournsize randomly chosen individuals, k times
    toolbox.register("select", tools.selTournament, tournsize=3)

    random.seed(64)

    pop = toolbox.population(n=300)
    # contains the best individual that ever lived in the population during the evolution
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    # keep the min from the whole population
    stats.register("min", np.min)

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=10,
                                   stats=stats, halloffame=hof, verbose=False)

    return log[-1]['min'], pop[-1]


def optimize_func(input_path, output_path, optimizer='both'):
    try:
        try:
            with open(input_path, 'r') as f:
                inp = json.load(f)
        except ValueError:
            print("Incorrect json format!")
        except OSError:
            print("Incorrect input path given!")

        inp = clean_input(inp)

        bounds = []
        min_cost = 0
        opt_tank_values = []

        for i in inp['tanks']:
            bounds.append((i["minimumVolume"], i["maximumVolume"]))

        if optimizer.lower() == 'de':
            print("Using Differential Evolution")
            result_de = differential_evolution(optimizer_function_de, bounds, args=(inp,), maxiter=1500,
                                               strategy="best1bin",
                                               popsize=20, seed=12, mutation=0.6, polish=True)

            min_cost, opt_tank_values = result_de['fun'], result_de['x']

        elif optimizer.lower() == 'deap':
            print("Using DEAP Genetic Algorithm")
            min_cost, opt_tank_values = deap_calculation(bounds, inp)


        elif optimizer.lower() == 'both':
            print("Using Both Differential Evolution and DEAP Genetic Algorithm")
            result_de = differential_evolution(optimizer_function_de, bounds, args=(inp,), maxiter=1500,
                                               strategy="best1bin",
                                               popsize=20, seed=12, mutation=0.6, polish=True)
            min_cost_de, opt_tank_values_de = result_de['fun'], result_de['x']

            min_cost_deap, opt_tank_values_deap = deap_calculation(bounds, inp)

            # take the min of deap and de commputed cost
            min_cost = min(min_cost_de, min_cost_deap)

            # select the minimum cost tank Volumes
            if min_cost_de < min_cost_deap:
                opt_tank_values = opt_tank_values_de

            elif min_cost_de > min_cost_deap:
                opt_tank_values = opt_tank_values_deap
            else:
                min_cost = min_cost_de
                opt_tank_values = opt_tank_values_de

        # calculate the optimized blend
        optimized_blend = calculate_optimized_blend(inp, opt_tank_values)
        inp["optimized_blend"] = optimized_blend

        # save the output in json file
        try:
            with open(output_path, 'w') as f:
                json.dump(inp, f)
        except ValueError:
            print("Incorrect input format!")
        except OSError:
            print("Incorrect output path given!")

        return min_cost, optimized_blend
    except Exception as e:
        print("Error - ", str(e))
