
def save_txt(file, name, metrics_scores, time):
    file.write(name+"\n")
    for name, score in metrics_scores.items():
        file.write(f"{name} = {score};({time})")
    file.write("\n\n")