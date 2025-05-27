import numpy as np
import pandas as pd

#normalization function
def normalize_data(scores, directions):
    min_vals = np.min(scores, axis=0)
    max_vals = np.max(scores, axis=0)
    range_vals = max_vals - min_vals
    range_vals[range_vals == 0] = 1  #avoid division by zero

    normalized_scores = np.zeros_like(scores, dtype=float)

    for i, direction in enumerate(directions):
        if direction == 'max':
            normalized_scores[:, i] = (scores[:, i] - min_vals[i]) / range_vals[i]
        elif direction == 'min':
            normalized_scores[:, i] = (max_vals[i] - scores[:, i]) / range_vals[i]
        else:
            normalized_scores[:, i] = 0.5 #if the values of the criteria are the same set 0.5

    return normalized_scores

#final score calculation
def calculate_final_scores(normalized_scores, weights):
    return np.dot(normalized_scores, weights)

#evaluation function
def evaluate_integration(strategies, weights, scores, directions):
    normalized_scores = normalize_data(scores, directions)
    final_scores = calculate_final_scores(normalized_scores, weights)
    return {strategies[i]: final_scores[i] for i in range(len(strategies))}

def save_results_to_csv(results, filename='results.csv'):
    df = pd.DataFrame(list(results.items()), columns=['Strategy', 'Final Score'])
    df.to_csv(filename, index=False)
