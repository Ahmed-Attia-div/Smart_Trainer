def recommend_rest_time(set_quality: str):
    if set_quality == "excellent":
        return 90
    elif set_quality == "good":
        return 60
    else:
        return 30
