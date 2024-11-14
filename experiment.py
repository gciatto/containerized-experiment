import openml
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import pickle
import os
from pathlib import Path


DATASET_ID = int(os.getenv('DATASET_ID', "61"))
TEST_SIZE = float(os.getenv('TEST_SIZE', "0.2"))
RANDOM_STATE = int(os.getenv('RANDOM_STATE', "42"))
K_FOLDS = int(os.getenv('K_FOLDS', "5"))
SCORING = os.getenv('SCORING', 'accuracy')
PICTURE_SIZE = tuple(map(int, os.getenv('PICTURE_SIZE', '10,6').split(',')))
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', '.'))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Load the Poker Hand dataset from OpenML
dataset = openml.datasets.get_dataset(DATASET_ID, download_all_files=True)  # iris
X, y, _, _ = dataset.get_data(target=dataset.default_target_attribute)

# Ensure test set contains at least one instance of each class
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE)

# Define classifiers and hyperparameters for GridSearchCV
classifiers = {
    'DecisionTree': (DecisionTreeClassifier(), {'max_depth': [None, 10, 20], 'min_samples_split': [2, 10, 20]}),
    'MLP': (MLPClassifier(), {'hidden_layer_sizes': [(50,), (100,), (50, 50)], 'activation': ['tanh', 'relu'], 'solver': ['adam', 'sgd']}),
    'LogisticRegression': (LogisticRegression(), {'C': [0.1, 1, 10], 'solver': ['liblinear', 'lbfgs']}),
    'SVM': (SVC(), {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']}),
}

# Run GridSearchCV for each classifier and store results
results = {}
best_estimators = {}

for clf_name, (clf, params) in classifiers.items():
    grid_search = GridSearchCV(clf, param_grid=params, cv=K_FOLDS, scoring=SCORING)
    grid_search.fit(X_train, y_train)
    
    # Save the cross-validation scores and best estimator
    results[clf_name] = grid_search.cv_results_['mean_test_score']
    best_estimators[clf_name] = grid_search.best_estimator_

# Compare validation performance with a boxplot
plt.figure(figsize=PICTURE_SIZE)
plt.boxplot(results.values(), labels=results.keys())
plt.title('Validation Set Performance of Models')
plt.ylabel('Accuracy')
plt.xlabel('Model')
plt.savefig(OUTPUT_DIR / 'graph.png')

# Select the best model and evaluate on test set
best_model_name = max(results, key=lambda k: max(results[k]))
best_model = best_estimators[best_model_name]
best_model.fit(X_train, y_train)

# Test set evaluation
y_pred = best_model.predict(X_test)
test_accuracy = accuracy_score(y_test, y_pred)

print(f'Best Model: {best_model_name}')
print(f'Test Set Accuracy: {test_accuracy:.4f}')


with open(OUTPUT_DIR / 'model.pkl', 'wb') as file:
    pickle.dump(best_model, file)
