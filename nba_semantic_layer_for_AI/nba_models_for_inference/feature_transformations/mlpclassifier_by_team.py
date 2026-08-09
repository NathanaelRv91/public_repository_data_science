# 1. Run A Local Session with Snowflake Connector to identity team/positional trends for the past 5 years in the NBA #
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report
from snowflake_data_connections import nba_eda_functions as nba

# 2. Load data from the REPORTS SCHEMA and place into our test/train datasets for EDA # 
nba_data = nba.pull_player_stats()
nba_data = pd.DataFrame(nba_data)

for i in range(len(nba_data)):
    if (nba_data.loc[i,"IS_GUARD"] == 1 & nba_data.loc[i, "IS_FORWARD"] == 1):
        nba_data.loc[i, "POSITION"] = "G"
    elif (nba_data.loc[i,"IS_FORWARD"] == 1 & nba_data.loc[i, "IS_CENTER"] == 1):
        nba_data.loc[i, "POSITION"] = "F"
    elif nba_data.loc[i,"IS_GUARD"] == 1:
        nba_data.loc[i, "POSITION"] = "G"
    elif nba_data.loc[i,"IS_FORWARD"] == 1:
        nba_data.loc[i, "POSITION"] = "F"
    elif nba_data.loc[i,"IS_CENTER"] == 1:
        nba_data.loc[i, "POSITION"] = "C"
    else: 
        nba_data.loc[i, "POSISION"] = "F"

X = nba_data[['TEAM_NAME','POSITION','YEAR_SEASON','ASSISTS_2026','BLOCKS_2026','DRB_2026','TRB_2026','ORB_2026','FGA_2026','FGM_2026']]
y = nba_data['POINTS_2026']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

mlp = MLPClassifier(
    hidden_layer_sizes=(100, 50), 
    activation='relu',           
    solver='adam',                
    max_iter=300,               
    random_state=42           
)

mlp.fit(X_train_scaled, y_train)
y_pred = mlp.predict(X_test_scaled)

print(f"Accuracy for NBA Data: {accuracy_score(y_test, y_pred):.2f}\n")
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=data.target_names))
