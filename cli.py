#!/usr/bin/env python3

import time

import click

from optimizer import optimize_func


@click.command()
@click.option('--input_path', default='files/input.json', help="Path of the input json")
@click.option('--output_path', default='files/output.json', help="Path to save output json")
@click.option('--optimizer', default='both', help="The optimizer to use [de,deap,both]")
def cli(input_path, output_path, optimizer):
    try:
        print('---Optimizing Inputs---')
        print()
        start_time = time.time()
        min_cost, opt_blend = optimize_func(input_path, output_path, optimizer)
        end_time = time.time()
        print("\t Cost : ", min_cost)
        print()
        print("---Optimized Blend---")
        print()
        for key, values in opt_blend.items():
            print("\t", key, " : ", values)
        print()
        print("--- %s seconds ---" % (end_time - start_time))
    except Exception as e:
        print("Error - ", str(e))


if __name__ == '__main__':
    cli()
