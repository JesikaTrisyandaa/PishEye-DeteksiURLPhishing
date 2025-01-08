import numpy as np
from collections import Counter

def gini_impurity(y):
    counts = np.bincount(y)
    probabilities = counts / len(y)
    return 1 - np.sum(probabilities ** 2)

def split_data(X, y, feature, threshold):
    left_mask = X[:, feature] <= threshold
    right_mask = ~left_mask
    return X[left_mask], y[left_mask], X[right_mask], y[right_mask]

class Node:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

class DecisionTree:
    def __init__(self, max_depth=None):
        self.max_depth = max_depth
        self.root = None

    def fit(self, X, y, depth=0):
        if len(set(y)) == 1 or depth == self.max_depth:
            return Node(value=Counter(y).most_common(1)[0][0])

        best_gini = float('inf')
        best_split = None

        n_features = X.shape[1]
        for feature in range(n_features):
            thresholds = np.unique(X[:, feature])
            for threshold in thresholds:
                X_left, y_left, X_right, y_right = split_data(X, y, feature, threshold)
                if len(y_left) == 0 or len(y_right) == 0:
                    continue

                gini = (len(y_left) / len(y)) * gini_impurity(y_left) + \
                       (len(y_right) / len(y)) * gini_impurity(y_right)

                if gini < best_gini:
                    best_gini = gini
                    best_split = (feature, threshold, X_left, y_left, X_right, y_right)

        if best_split is None:
            return Node(value=Counter(y).most_common(1)[0][0])

        feature, threshold, X_left, y_left, X_right, y_right = best_split
        left_child = self.fit(X_left, y_left, depth + 1)
        right_child = self.fit(X_right, y_right, depth + 1)
        return Node(feature, threshold, left_child, right_child)

    def predict_one(self, x, node):
        if node.value is not None:
            return node.value
        if x[node.feature] <= node.threshold:
            return self.predict_one(x, node.left)
        else:
            return self.predict_one(x, node.right)

    def predict(self, X):
        return np.array([self.predict_one(x, self.root) for x in X])

class RandomForest:
    def __init__(self, n_trees=10, max_depth=7):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.trees = []

    def fit(self, X, y):
        self.n_features_in_ = X.shape[1]
        for _ in range(self.n_trees):
            indices = np.random.choice(len(X), len(X), replace=True)
            X_sample = X[indices]
            y_sample = y[indices]
            tree = DecisionTree(max_depth=self.max_depth)
            tree.root = tree.fit(X_sample, y_sample)
            self.trees.append(tree)

    def predict(self, X):
        predictions = np.array([tree.predict(X) for tree in self.trees])
        final_predictions = [Counter(col).most_common(1)[0][0] for col in predictions.T]
        return np.array(final_predictions)
