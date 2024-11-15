import openml
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import pickle
import os
from pathlib import Path
from hashlib import sha512
import yaml
import sys


def get_grid_search_entry_from_env(env_var_name):
    if env_var_name.startswith('MODEL_'):
        name = env_var_name[len('MODEL_'):]
    else:
        name = env_var_name
        env_var_name = f'MODEL_{name}'
    hyperparams = os.environ[env_var_name]
    hyperparams = yaml.safe_load(hyperparams)
    assert len(hyperparams) == 1, f"Too many keys in {env_var_name}"
    for k, v in hyperparams.items():
        return {name: [k, v]}


def get_grid_search_entries_from_env():
    entries = {}
    for k in os.environ:
        if k.startswith('MODEL_'):
            for name, params in get_grid_search_entry_from_env(k).items():
                entries[name] = params
    return entries


def create_scikit_learn_model(class_name):
    import importlib
    module_name, class_name = class_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    klass = getattr(module, class_name)
    return klass()


# Set up environment hyper-parameters from the environment, with safe defaults
DATASET_ID = int(os.getenv('DATASET_ID', "61"))
TEST_SIZE = float(os.getenv('TEST_SIZE', "0.2"))
RANDOM_STATE = int(os.getenv('RANDOM_STATE', "42"))
K_FOLDS = int(os.getenv('K_FOLDS', "5"))
SCORING = os.getenv('SCORING', 'accuracy')
PICTURE_SIZE = tuple(map(int, os.getenv('PICTURE_SIZE', '10,6').split(',')))
MODELS = get_grid_search_entries_from_env()

# Compute a unique experiment ID based on the hyper-parameters
FOOTPRINT_KEYS = {'DATASET_ID', 'TEST_SIZE', 'RANDOM_STATE', 'K_FOLDS', 'SCORING', 'PICTURE_SIZE', 'MODELS'}
EXPERIMENT_FOOTPRINT = {k: v for k, v in locals().items() if k in FOOTPRINT_KEYS}
EXPERIMENT_FOOTPRINT_YAML = yaml.dump(EXPERIMENT_FOOTPRINT, sort_keys=True)
EXPERIMENT_ID = sha512(EXPERIMENT_FOOTPRINT_YAML.encode()).hexdigest()

# Ensure the output directory exists
DATA_DIR = Path(os.getenv('DATA_DIR', './data'))
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', str(DATA_DIR)))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Do not waste time if the experiment has already been run
# by looking for the existence of a .yaml file named after the EXPERIMENT_ID
for file in DATA_DIR.glob('**/*.yaml'):
    if file.is_file() and file.stem == EXPERIMENT_ID:
        print(f'Experiment with ID {EXPERIMENT_ID[:8]} already exists in {file.parent}', file=sys.stderr)
        exit(0)


print(f'Running experiment ID {EXPERIMENT_ID[:8]}', file=sys.stderr)
print(f'Output directory: {OUTPUT_DIR}', file=sys.stderr)
print(f'Experiment footprint:\n\t{EXPERIMENT_FOOTPRINT_YAML.replace("\n", "\n\t")}', file=sys.stderr)


# Load the Poker Hand dataset from OpenML
dataset = openml.datasets.get_dataset(DATASET_ID, download_all_files=True)
X, y, _, _ = dataset.get_data(target=dataset.default_target_attribute)

# Ensure test set contains at least one instance of each class
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE)

# Define classifiers and hyperparameters for GridSearchCV
classifiers = {name: (create_scikit_learn_model(params[0]),) + tuple(params[1:]) for name, params in MODELS.items()}
print(f'Start GridSearchCV for the following models/parameters: {classifiers}', file=sys.stderr)

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
# Save the plot to OUTPUT_DIR/graph.png
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

# Save the best model to OUTPUT_DIR/model.pkl
with open(OUTPUT_DIR / 'model.pkl', 'wb') as file:
    pickle.dump(best_model, file)


# Save experiment footprint into OUTPUT_DIR/EXPERIMENT_ID.yaml
with open(OUTPUT_DIR / f'{EXPERIMENT_ID}.yaml', 'w') as file:
    yaml.dump(EXPERIMENT_FOOTPRINT, file)
