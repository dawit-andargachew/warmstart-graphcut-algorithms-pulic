"""
This file is used to take the average of the cold-/warm-start running time and the statistics
such as # of paths taken and average path lengths.
"""

import numpy as np
import argparse
import os
import glob

def mstd(row):
    return (np.mean(row), np.std(row))

def collect_result_files(result_dir, size, file_type):
    """
    Collect all result files matching the pattern {size}_{file_type}_*.txt
    and combine their data.
    """
    pattern = "{}/{}_{}_*.txt".format(result_dir, size, file_type)
    files = sorted(glob.glob(pattern))
    
    if not files:
        # Fallback to old naming pattern
        old_file = "{}/{}_{}.txt".format(result_dir, size, file_type)
        if os.path.exists(old_file):
            files = [old_file]
    
    all_data = []
    for file_path in files:
        with open(file_path, 'r') as f:
            lines = f.readlines()[1:]  # Skip header
            for line in lines:
                if line.strip():  # Skip empty lines
                    all_data.append(line.split('\t')[1:])  # Skip image_name column
    
    return np.array(all_data, dtype=np.float64) if all_data else None

parser = argparse.ArgumentParser(description='Average experiment results')
parser.add_argument('-g', '--group', type=str, choices=["birdhouse", "head", "shoe", "dog"],
                    help='Image group name (optional, processes all groups if not specified)')
parser.add_argument('-s', '--size', type=int, choices=[30, 60, 120],
                    help='Image size (optional, processes all sizes if not specified)')

args = parser.parse_args()

groups = [args.group] if args.group else ["birdhouse", "head", "shoe", "dog"]
sizes = [args.size] if args.size else [30, 60, 120]

time_average_dir = "./sequential_datasets/all_time_averages.txt"
path_average_dir = "./sequential_datasets/all_path_averages.txt"
time_average_f = open(time_average_dir, 'w')
path_average_f = open(path_average_dir, 'w')  # Fixed bug: was using time_average_dir
time_titles = "image_group\tsize\tff\twarm_start\tfeas_proj\tratio(%)\n"
time_average_f.write(time_titles)
path_titles = "image_group\tsize\texcess_ratio\trecoverd_flow_ratio\tnum_aug_path_avg\tavg_path_len\tnum_proj_path_avg\tavg_proj_len\tnum_warm_start_path_avg\tavg_warm_start_len\n"
path_average_f.write(path_titles)

for group in groups:
    for size in sizes:
        result_dir = "./sequential_datasets/{}_results".format(group)
        
        if not os.path.exists(result_dir):
            print(f"Warning: Result directory {result_dir} does not exist. Skipping.")
            continue
        
        time_data = collect_result_files(result_dir, size, "time")
        path_data = collect_result_files(result_dir, size, "path")
        
        if time_data is None or len(time_data) == 0:
            print(f"Warning: No time data found for {group} size {size}. Skipping.")
            continue
        
        if path_data is None or len(path_data) == 0:
            print(f"Warning: No path data found for {group} size {size}. Skipping.")
            continue

        time_average_f.write('{}\t{}\t'.format(group, size))
        path_average_f.write('{}\t{}\t'.format(group, size))

        time_average = np.average(time_data, axis=0)

        for time in time_average:
            time_average_f.write(str(round(time, 2)) + '\t')
        time_average_f.write(str(round(1 - time_average[1] / time_average[0], 4)) + '\n')

        path_averages = []
        # Calculate ratios with safety check
        if np.any(path_data[:, 0] != 0):  # Check if flow_value is not all zero
            path_process = np.divide(path_data[:, 1:3].T, path_data[:, 0])
            path_averages.extend([mstd(path_process[0]), mstd(path_process[1])])
        else:
            path_averages.extend([(0, 0), (0, 0)])  # Default values if flow_value is zero

        for i in range(3, 9):
            if i < path_data.shape[1]:
                path_averages.append(mstd(path_data[:, i]))
            else:
                path_averages.append((0, 0))
        
        for avg in path_averages:
            path_average_f.write("({}, {})\t".format(round(avg[0], 2), round(avg[1], 2)))
        path_average_f.write("\n")

time_average_f.close()
path_average_f.close()
print(f"Results written to {time_average_dir} and {path_average_dir}")






