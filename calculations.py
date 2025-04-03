import numpy as np
import pandas as pd

#normalization function
def normalize_data(scores):
    min_vals = np.min(scores, axis=0)
    max_vals = np.max(scores, axis=0)
    range_vals = max_vals - min_vals

    range_vals[range_vals == 0] = 1
    normalized_scores = (scores - min_vals) / range_vals

    normalized_scores[:, range_vals == 1] = 0.5  #if the value of the criteria is the same set 0.5

    return normalized_scores

#final scrore calculation function
def calculate_final_scores(normalized_scores, weights):
    final_scores = np.dot(normalized_scores, weights)
    return final_scores

#evaluation integration function
def evaluate_integration(strategies, weights, scores):
    normalized_scores = normalize_data(scores)
    final_scores = calculate_final_scores(normalized_scores, weights)
    return {strategies[i]: final_scores[i] for i in range(len(strategies))}

#CVS results saving
def save_results_to_csv(results, filename='results.csv'):
    df = pd.DataFrame(list(results.items()), columns=['Strategy', 'Final Score'])
    df.to_csv(filename, index=False)