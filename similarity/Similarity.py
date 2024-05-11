import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class SimilarityCalculator:
    def __init__(self, data):
        self.data = data
    
    def compute_cosine_similarity(self):
        # Compute cosine similarity between rows of the dataframe
        similarity_matrix = cosine_similarity(self.data)
        return similarity_matrix
    
    def compute_euclidean_distance(self):
        # Compute Euclidean distance between rows of the dataframe
        distance_matrix = pd.DataFrame(index=self.data.index, columns=self.data.index)
        for i in range(len(self.data)):
            for j in range(len(self.data)):
                distance_matrix.iloc[i, j] = np.linalg.norm(self.data.iloc[i] - self.data.iloc[j])
        return distance_matrix
    
    def compute_jaccard_similarity(self):
        # Compute Jaccard similarity between rows of the dataframe
        similarity_matrix = pd.DataFrame(index=self.data.index, columns=self.data.index)
        for i in range(len(self.data)):
            for j in range(len(self.data)):
                intersection = len(set(self.data.iloc[i]) & set(self.data.iloc[j]))
                union = len(set(self.data.iloc[i]) | set(self.data.iloc[j]))
                similarity_matrix.iloc[i, j] = intersection / union
        return similarity_matrix
    
