# Introduction

This project aims, to increase performance related to the Label Propagation problem on hypergraphs.
Specifically, the computation takes place on a machine with NUMA architecture called Furore.
The software runs with OpenMP to work in a parallel manner on shared memory.
The content involves a script in Python to evaluate the performance of the program written in C++ in order to assess what is the best configuration for environment variables and computation directives and increase performance.

# Furore

The NUMA Furore machine consists of two Numa Nodes and each node includes 32 CPU s Intel(R) Xeon(R) Gold 5218
(16 cores per processor) with 2 threads per core.
The operating system installed is Ubuntu 20.04.4 LTS.
The algorithm for the label propagation was written in
C++17 and we used GCC 10.3.0 as a compiler.

# Construction of the hypergraph

For the construction of the hypegraph, you can use the bash script repreceivable at the following path:

``` bash
Hpc-LabelPropagation-Project
    |-- LabelPropagation-C++
        |-- tools/
            |-- generate_hg.sh
```   

For this file, it is possible to specify how many vertices and arcs the hypergraph should have and how dense it should be in terms of links between nodes.
You can change these values in this part of the code:

```
#!/bin/bash
DEST_DIR="../resources/"

vertices=(5000)
edges=(300)
perc_vertices=(50)
```

After choosing the appropriate values, you can run the generation script, which will create the corresponding text file, as follow:
```
./generate_hg.sh
 ```

Here is also provided the file used by us.

# Prerequisites

To reproduce the results, one must create the directories with the code below in the directory /home/hpc2/Hpc-LabelPropagation-Project/LabelPropagation-C++/src/code, then compile it with CMake. Generate the hypergraph on which to run and then run the Python script.
Keep in mind that the results may vary, as they depend on nondeterministic elements, such as how the operating system chooses to schedule the execution.

### Benchmarks without partitioning 

The code we used was located in /home/hpc2/Hpc-LabelPropagation-Project/LabelPropagation-C++/src/code/opt_5, here is located in code\opt_5.
To change the scheduling directives for computation instead, go to the following path:
```
/home/hpc2/Hpc-LabelPropagation-Project/LabelPropagation-C++/src/code/opt_5/label_propagation.cpp
```
Change the value of the directives like this:
```

#pragma omp parallel
        {
            #pragma omp for private(current_edge) nowait //schedule(clause) used when trying different schedule clauses
            for (int i = 0; i < num_edge; i++)
            {
               ...
            }

AND ALSO CHANGE THIS!

 #pragma omp for private(new_label, current_vertex) nowait //schedule(clause) used when trying different schedule clauses
            for (int i = 0; i < num_vertex; i++)
            {
                ...
            }
```

### Benchmarks with partitioning

The code we used was located in /home/hpc2/Hpc-LabelPropagation-Project/LabelPropagation-C++/src/code/opt_6,  here is located in code\opt_6.
To change the scheduling directives for the initialization part, you have to go to the C++ utils file, found at the following path:
 ```
 /home/hpc2/Hpc-LabelPropagation-Project/LabelPropagation-C++/src/benchmarks/utils.hpp
 ```

When testing the code with hypergraph partitioning, change the initialization directives enter a different value in the round brackets, as follows:
```
	HyperGraph *hg = new HyperGraph(num_vertices, num_edges);
	//Read the edges and write it to the HyperGraph	
	/*#pragma omp parallel insert this pragma
	{
		#pragma omp for schedule(clause) change with the preferred clause*/ 
		for (int i = 0; i < num_vertices; i++)
		{
			for (int j = vertices_offsets[i]; (i < num_vertices - 1) ? j < vertices_offsets[i + 1] : j < data_size; j++)
			{
				...
			}
		}
	//}
```

To change the scheduling directives for computation instead, go to the following path:
```
/home/hpc2/Hpc-LabelPropagation-Project/LabelPropagation-C++/src/code/opt_6/label_propagation.cpp
```
Change the value of the directives like this:
```

 #pragma omp parallel
        {
            #pragma omp for private(current_edge) nowait //schedule(clause) here the clause you want
            for (int i = 0; i < num_edge/2; i++)
            {
                ...
            }

            #pragma omp for private(current_edge) nowait //schedule(clause) here the clause you want
            for (int i = num_edge/2; i < num_edge; i++)
            {
                ...
            }

AND ALSO CHANGE THIS!

 #pragma omp for private(new_label, current_vertex) nowait //schedule(clause) here the clause you want
            for (int i = 0; i < num_vertex/2; i++)
            {
                ...
            }

            #pragma omp for private(new_label, current_vertex) nowait //schedule(clause) here the clause you want
            for (int i = num_vertex/2; i < num_vertex; i++)
            {
                ...
            }
```

# Script Python 

The python file handles the execution of C++ code for label propagation and stores the execution times in specially created files.
Execution involves changing configurations to find out which one is best. The elements that vary are these:
- The PLACES and PROC_BINDINGS directives.
- The number of threads involved in the computation

The script takes as input a text file representing the hypergraph in terms of vertices (as generated in the section above), nodes and links and executes the C++ code 10 times for the same configuration.
Once the executions are completed for each configuration, it stores the execution times, to calculate mean, variance and median.
It also takes care of analyzing and storing the values of the perf tool, which is a profiling tool for numa architectures.

To reproduce the execution, one must simply launch the python file by entering the path to the label propagation code in this code section (in our case benchmark_opt_3 for the original code, benchmark_opt_5 for the benchmarks without partitioning and then benchmark_opt_6 for the benchmarks with partitioning):

 ```
 program = './benchmark_opt_3' #when testing the original code
 program = './benchmark_opt_5' #when testing only the pragmas
 program = ['perf', 'stat', '-e', 'node-loads', '-e', 'node-stores', '-e', 'node-loads-misses', '-e', 'node-stores-misses', '-o', output_perf, '--append', './benchmark_opt_6', input_file] #with partitioning
 ```

 To run the Python script you need to copy it to the following path:
 ```
 /home/hpc2/Hpc-LabelPropagation-Project/LabelPropagation-C++/build/bin
 ```
 To launch the script, type:
 ```
 python3 bench.py
 ```

The results will be collected and inserted via the script into a text file that can be found in the same directory as the script and will have name equal to the number of vertices, arcs and densities chosen from the hypergraph construction file, followed by the string 'result'
In the output file you will find:
- Configuration parameters used
- For each configuration, you will find the mean, median and variance values in terms of time (milliseconds)
- Profiling statistics generated by the tool perf.

# Achievements in brief

When the script has finished running, you will be able to see which configuration turned out best.
In our case, the best one involved setting the following parameters:
- Number of threads used in the computation 32.
- OMP_PLACES must be set to 'core'
- OMP_PROC_BINDINGS must be set to 'spread'
- Label propagation initialization and computation must have OpenMP scheduling directives set to 'dynamic'.


This configuration produced a 28% performance improvement over baseline (without changes to the label propagation code and without setting environment variables).
 