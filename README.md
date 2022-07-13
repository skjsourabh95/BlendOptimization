# Blend optimization
- A cmd tool that reads a input json file with relevant details provided and  optimizes oil blend amounts to get the desired oil blend quality at the lowest price saving the result in a json file.

## Tech Stack
- [Anaconda Python3](https://www.anaconda.com/distribution/) or [Python3](https://www.python.org/downloads/)
- [Deap](https://github.com/DEAP/deap)
- [Scipy](https://scipy.org/)


## Input & Output
```
If you have the `input.json` file already, place it in the files folder.
Otherwise, you can also give the path to the input file in the cmd arguments.
eg., D:\abc\topgear\APOPHIS_blender\input.json
Once processed by default the file is stored in the files folder.
Otherwise, you can also give the path to the output file in the cmd arguments.
eg., D:\abc\topgear\APOPHIS_blender\output.json
[NOTE] - A already processed input and output file is present in the files directory for reference.
```

## Installing and running locally
Run the following commands -
```
conda create -n aphosis python==3.7 -y
conda activate aphosis
cd /path/to/project/requirements.txt
pip install -r requirements.txt
python cli.py
```

## cli.py arguments:
```
- '--help' - Outputs information on all other commands/parameters.
- '--input_path', default='files/input.json',Path of the input json.
- '--output_path', default='files/output.json', Path to save output json.
- '--optimizer', default='both', The optimizer to use [de,deap,both].
[NOTE] - To understand how this arguments are used please follow solution.md 
```
## Verification
The command-line tool can be used to verify the entire optimization process.
To run the solution on a input json run the following commands:
```bash
python cli.py 
python cli.py --optimizer=deap
python cli.py --optimizer=de
```
This is also show the time taken by the solution so that it call help the reviews better.
The video of the solution with all options could be found [here](https://drive.google.com/file/d/11ZJUHp1mbzU0NLbQWguShvZu4zvwXyrr/view?usp=sharing)<br>
[Note] - For better understanding of the solution please read solution.md

## Differntial Evolution
- The idea behind the differential evolution method was taken from [here](http://www1.icsi.berkeley.edu/~storn/code.html).
- The code used is from scipy where all the required hyper-parameters are already tuned to take the best possible arrangement.

```cmd
# Running the Differntial Evolution Algorithm-
python cli.py --optimizer=de
```
```html
Output - 
---Optimizing Inputs---

Using Differential Evolution
         Cost :  6.237241404869348

---Optimized Blend---

         Volume  :  120590.8647491185
         totalMt  :  19338.20709456086
         specificGravity  :  1.0107016903125892
         API  :  8.501744685157263
         Viscosity  :  427.5421550559299
         Cost  :  1.0002172738130664
         SulfurPcnt  :  2.038244669393788
         Flash  :  214.72411401143518
         WaterPcnt  :  0.35371038341871053
         AsphPcnt  :  0.0
         AlSi  :  24.99406578666964
         Si  :  0.0
         V  :  198.55071022757062
         Na  :  8.849833368478293
         MCRTPcnt  :  12.855977911821032
         Density  :  1010.1
         CCAI  :  675.0580101558562

--- 2.248988151550293 seconds ---
```

## DEAP Genetic Algorithm
- The idea behind this algorithm was taken from  [here](https://deap.readthedocs.io/en/master/examples/ga_onemax_short.html#short-ga-onemax)
- The code was modified to work according to our objective function and the given constraints.
- The code is being utilised from DEAP framework.
- The Algorithm utiises HallOfFrame approach which is -<br>
The hall of fame contains the best individual that ever lived in the population during the evolution. It is lexicographically sorted at all time so that the first element of the hall of fame is the individual that has the best first fitness value ever seen, according to the weights provided to the fitness at creation time.
- The main runner alogorithm in this is - `eaSimple`

```This algorithm reproduces the simplest evolutionary algorithm.
The algorithm goes as follow -
First, it evaluates the individuals with an invalid fitness. 
Second, it enters the generational loop where the selection procedure is applied to entirely replace the parental population.
Third, it applies the varAnd() function to produce the next generation population.
Fourth, it evaluates the new individuals and compute the statistics on this population. 
Finally, when ngen generations are done, the algorithm returns a tuple with the final population.
```


```cmd
# Running the DEAP Algorithm-
python cli.py --optimizer=deap
```
```html
Output - 
---Optimizing Inputs---

Using DEAP Genetic Algorithm
         Cost :  6.235893759249139

---Optimized Blend---

         Volume  :  142734.21461206206
         totalMt  :  22871.172816254526
         specificGravity  :  1.009908319349816
         API  :  8.611728251826264
         Viscosity  :  426.2126177913449
         Cost  :  1.0
         SulfurPcnt  :  2.034739480982902
         Flash  :  215.4611379324664
         WaterPcnt  :  0.35951853270819273
         AsphPcnt  :  0.0
         AlSi  :  24.926981913745205
         Si  :  0.0
         V  :  201.609649714585
         Na  :  8.907975391970004
         MCRTPcnt  :  12.748869601777248
         Density  :  1009.3000000000001
         CCAI  :  674.3303518879327

--- 0.6522560119628906 seconds ---
```

## BEST of Both Algorithms
- 
```cmd
# Running the both Algorithms
python cli.py
```
```html
Output - 
---Optimizing Inputs---

Using Both Differential Evolution and DEAP Genetic Algorithm
         Cost :  6.235893759249139

---Optimized Blend---

         Volume  :  142734.21461206206
         totalMt  :  22871.172816254526
         specificGravity  :  1.009908319349816
         API  :  8.611728251826264
         Viscosity  :  426.2126177913449
         Cost  :  1.0
         SulfurPcnt  :  2.034739480982902
         Flash  :  215.4611379324664
         WaterPcnt  :  0.35951853270819273
         AsphPcnt  :  0.0
         AlSi  :  24.926981913745205
         Si  :  0.0
         V  :  201.609649714585
         Na  :  8.907975391970004
         MCRTPcnt  :  12.748869601777248
         Density  :  1009.3000000000001
         CCAI  :  674.3303518879327

--- 2.941136360168457 seconds ---
```


