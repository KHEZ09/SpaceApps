import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Expect a CSV with columns: pm25, temp, humidity, wind_speed, target_pm25
df = pd.read_csv("data/sample_aq_bogota.csv")
X = df[["pm25","temp","humidity","wind_speed"]]
y = df["target_pm25"]
X_train, X_val, y_train, y_val = train_test_split(X,y,test_size=0.2,random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
joblib.dump(model, "model/model.pkl")
print("Saved model to model/model.pkl")
#a