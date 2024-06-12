import json
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import numpy as np
from symbols_sig.collection_info import SymbolsSigCollector
from framework.config import *
from framework.job_master import *
from framework.database import *
from framework.collections import *
from common.operators import map_bysym

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

def _fit_curve(points: list[tuple[float, float]], make_photo: str | None = None) -> float:
    """y(x) = alpha / x + (1 - alpha)"""
    
    # Initial guess for 'a'
    initial_guess = 1.0

    if points[0][0] != 1:
        print(f"warning: points list should start with '1' for correct normalization!")

    norm_y = points[0][1]
    normalized_points = [(x, y/norm_y) for x, y in points]

    curve = TargetFunc(normalized_points, lambda x, alpha: alpha / x + (1 - alpha))

    # Perform optimization to minimize the objective function
    result = minimize(curve, initial_guess)

    # Extract the optimized value of 'a'
    # optimized_a = result.x[0]
    optimized_a = result.x[0]

    max_x = points[-1][0]

    if isinstance(make_photo, str):
        x_values = np.linspace(0.3, max_x*1.5, 100)  # Generate x values for plotting
        y_values = optimized_a / x_values + (1 - optimized_a)  # Calculate y values for the curve

        plt.figure(figsize=(8, 6))
        plt.scatter(*zip(*normalized_points), label='Data Points')
        plt.plot(x_values, y_values, color='red', label='Fitted Curve')
        plt.xlabel('Num Threads')
        plt.ylabel('Average IPC')
        plt.title(f'Alpha = {optimized_a:.3f}, Loss = {curve(optimized_a):.3f}')
        plt.legend()
        plt.grid(True)
        plt.savefig(make_photo)

    return optimized_a

def _get_first(iterable):
    for item in iterable:
        return item

def _collect_alpha(master: JobMaster, config: Config) -> object:    
    sig_configs = [
        SymbolsSigCollector.create_config(config.exe_path, count, config.num_reps)
        for count in config.thread_counts
    ]
    sig_ids: list[int] = [_get_first(master.satisfy(sig_conf)) for sig_conf in sig_configs]
    sig_results: list[object] = [master.db.get(res_id) for res_id in sig_ids]
    
    results = []
    for sym, by_thread_count in map_bysym(sig_results).items():
        coords = [(thread_count, sig["avg_ipc"]) for sig, thread_count in zip(by_thread_count, config.thread_counts)]
        png_fname = f"./graphs/{sym}-t{'_'.join(map(str, config.thread_counts))}.png"
        alpha = _fit_curve(coords, png_fname)
        results.append({
            "symbol": sym,
            "alpha": alpha
        })

    return results

class SymbolsAlphaCollector(Collector):
    def get_field_names(self) -> list[str]:
        return [
            "exe_path",
            "thread_counts",
            "num_reps",
            "conf_type"
        ]

    def get_collector(self) -> Callable:
        return _collect_alpha

    def create_config(exe_path: str, thread_counts: list[int], num_reps: int) -> Config:
        return Config({
            "conf_type": "symbols_alpha",
            "exe_path": exe_path,
            "thread_counts": thread_counts,
            "num_reps": num_reps,
        })

if __name__ == "__main__":
    print(_fit_curve([(1, 8), (2, 5), (4, 3), (8, 2)]))