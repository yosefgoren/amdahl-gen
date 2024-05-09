import json, jsonschema
# from significant.collect import collect_significant
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import numpy as np

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

def collect_alpha(config: object) -> object:
    jsonschema.validate(config, json.load(open("alpha.config.schema.json")))
    sig_configs = [{
        "exe-path": config["exe-path"],
        "thread-count": count,
        "repetitions": config["num-reps"]
    } for count in config["thread-counts"]]
    results = [collect_significant(sig_conf) for sig_conf in sig_configs]
    
    all_line_numbers = _setsum([set(res["data"].keys()) for res in results])
    # TODO: verify all have every line numbers?
    alphas_by_line = dict()
    for lineno in all_line_numbers:
        line_runtimes = [res["data"][lineno] for res in results]
        line_curve_points = zip(config["thread-counts"], line_runtimes)
        alphas_by_line[lineno] = _fit_curve(line_curve_points)

    return alphas_by_line

if __name__ == "__main__":
    print(_fit_curve([(1, 8), (2, 5), (4, 3), (8, 2)]))