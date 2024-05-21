import json
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import numpy as np
from framework.config import *
from framework.job_master import *
from framework.database import *
from framework.collections import *

class TargetFunc:
    def __init__(self, points, formula):
        self.points = points
        self.formula = formula

    def __call__(self, alpha):
        total_error = 0
        for x, y in self.points:
            predicted_y = self.formula(x, alpha) 
            error = (y - predicted_y) ** 2
            total_error += error
        return total_error

def _fit_curve(points: list[tuple[float, float]]) -> float:
    """runtime_alpha(t) = alpha / x + (1 - alpha)"""
    
    # Initial guess for 'a'
    initial_guess = 1.0

    if points[0][0] != 1:
        print(f"Error: points list must start with '1' for normalization!")
        exit(1)

    basetime = points[0][1]
    normalized_points = [(nt, runtime/basetime) for nt, runtime in points]

    curve = TargetFunc(normalized_points, lambda x, alpha: alpha / x + (1 - alpha))

    # Perform optimization to minimize the objective function
    result = minimize(curve, initial_guess)

    # Extract the optimized value of 'a'
    optimized_a = result.x[0]
    # Plotting the curve
    
    x_values = np.linspace(0.1, 10, 100)  # Generate x values for plotting
    y_values = optimized_a / x_values + (1 - optimized_a)  # Calculate y values for the curve

    plt.figure(figsize=(8, 6))
    plt.scatter(*zip(*normalized_points), label='Data Points')
    plt.plot(x_values, y_values, color='red', label='Fitted Curve')
    plt.xlabel('Num Threads')
    plt.ylabel('Runtime')
    plt.title(f'Alpha = {optimized_a:.3f}, Loss = {curve(optimized_a):.3f}')
    plt.legend()
    plt.grid(True)
    plt.savefig('out.png')

def _setsum(sets: list[set]) -> set:
    res = set()
    for s in sets:
        res += s
    return res

def _collect_alpha(master: JobMaster, config: Config) -> object:    
    sig_configs = [
        Config.create_significant(config["exe_path"], count, config["num_reps"])
        for count in config["thread_counts"]
    ]
    result_ids: list[int] = [list(master.db.get(master.satisfy(sig_conf))[0]) for sig_conf in sig_configs]
    results: list[object] = [master.db.get(res_id) for res_id in result_ids]
    
    all_line_numbers = _setsum([set(res["data"].keys()) for res in results])
    # TODO: verify all have every line numbers?
    alphas_by_line = dict()
    for lineno in all_line_numbers:
        line_runtimes = [res["data"][lineno] for res in results]
        line_curve_points = zip(config["thread_counts"], line_runtimes)
        alphas_by_line[lineno] = _fit_curve(line_curve_points)

    return alphas_by_line

class AlphaCollector(Collector):
    def get_field_names(self) -> list[str]:
        return [
            "exe_path",
            "thread_counts",
            "num_reps",
            "conf_type"
        ]

    def get_collector(self) -> Callable:
        return _collect_alpha

    def create_config(exe_path: str, thread_count: int, num_reps: int) -> Config:
        return Config({
            "conf_type": "significant",
            "exe_path": exe_path,
            "thread_count": thread_count,
            "num_reps": num_reps,
        })

if __name__ == "__main__":
    print(_fit_curve([(1, 8), (2, 5), (4, 3), (8, 2)]))