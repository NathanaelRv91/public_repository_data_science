# 1. Run A Local Session with Snowflake Connector to identity team/positional trends for the past 5 years in the NBA #
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

# 2. Load data from the REPORTS SCHEMA and place into our test/train datasets for EDA # 

X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

mlp = MLPClassifier(
    hidden_layer_sizes=(100, 50), # 2 hidden layers: 100 nodes, then 50 nodes
    activation='relu',            # Rectified Linear Unit activation function
    solver='adam',                # Optimization algorithm
    max_iter=300,                 # Maximum number of epochs
    random_state=42               # Ensures reproducible results
)

mlp.fit(X_train_scaled, y_train)
y_pred = mlp.predict(X_test_scaled)

print(f"Accuracy for NBA Data: {accuracy_score(y_test, y_pred):.2f}\n")
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=data.target_names))
