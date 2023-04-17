import json
import os

import requests
from pandas import read_csv

# Read the CSV file with the sessions
df_sessions = read_csv("s3/sessions.csv", low_memory=False, index_col=0)

# Select a random session and prepare the data for prediction
session_id = df_sessions["session_id"].sample(1).values
predict_session = set(session_id)
df_predict = df_sessions[df_sessions["session_id"].isin(predict_session)].copy()
df_predict = df_predict.sort_values(by="position_in_list").copy()
is_new_user = df_predict["is_new_user"].unique()[0]
data = df_predict[["venue_id", "is_from_order_again", "is_recommended"]].values.tolist()
purchased = df_predict[df_predict.purchased == 1]["venue_id"].values[0]

# Send a POST request to the local server with the data to predict the ranking of the purchased venue
url = f"http://localhost:{os.getenv('APP_PORT',1111)}/predict?is_new_user={is_new_user}"
headers = {"accept": "application/json", "Content-Type": "application/json"}
payload = [
    {"venue_id": venue_id, "is_from_order_again": is_from_order_again, "is_recommended": is_recommended}
    for venue_id, is_from_order_again, is_recommended in data
]
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Retrieve the ranked venues from the prediction response and find the position of the purchased venue
venues_and_scores = response.json()["venues_and_scores"]
ordered_venues = sorted(venues_and_scores, key=lambda x: x["score"], reverse=True)
for i, venue in enumerate(ordered_venues):
    if venue["venue_id"] != purchased:
        continue
    print(f"Purchased venue was ranked as {i + 1} element of {len(ordered_venues)}")
    break
