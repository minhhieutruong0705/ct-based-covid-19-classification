# -*- coding: utf-8 -*-
"""Covid19_Phase2_ResultProcessing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-f8clPc3GgnfdQYPCwjjBEJ9PkDpHNqY
"""

# %cd ~/Minh\ Hieu

# Commented out IPython magic to ensure Python compatibility.
# %cd /media/truong/New Volume/DONE/Projects/Covid CT-base Classification/Implementation/2. Binary Classification

import numpy as np
import math

## Copy from VisualFinal
def get_scores(data, key):
  data_class = []
  data_mask = []
  signal = "STOP"

  for line in data:
    line = line.strip()
    if signal == "START":
      if "[Classification]" in line:
        elements = line.split(",")
        scores_class = [float(element.split(" ")[-1]) for element in elements]
        data_class.append(scores_class)
      if "[Segmentation]" in line:
        elements = line.split(",")
        scores_mask = [float(element.split(" ")[-1]) for element in elements]
        data_mask.append(scores_mask)
        signal = "STOP"
    if key in line:
      signal = "START"
      epoch = int((line.split(" ")[-1])[:-1])

  return np.array(data_class), np.array(data_mask)

## Copy from VisualFinal
def parse_data (file_path):
  file = open(file_path, "r")
  data = file.read().split("\n")[1:]
  file.close()

  train_data_class, train_data_mask = get_scores(data, "[TRAIN]")
  eval_data_class, eval_data_mask = get_scores(data, "[EVAL]")
  test_data_class, test_data_mask = get_scores(data, "[TEST]")

  return train_data_class, train_data_mask, eval_data_class, eval_data_mask, test_data_class, test_data_mask

def process_result(data, out_file_path):
  PROCESSING_RANGE_SEGMENTATION = 30
  PROCESSING_RANGE_CLASSIFICATION = 80
  LABELS = ["Classification Accuracy (Test)", "Classification Dice Score (Test)", "Classification F1 (Test)",
            "Segmentation Accuracy (Test)", "Segmentation Dice Score (Test)"]
  
  f = open(out_file_path, "w")
  for i in range(data.shape[1]):
    scores = data[:, i]
    if "F1" in LABELS[i]:
      scores = scores * 100
    if "Classification" in LABELS[i]:
      print(f"{LABELS[i]}:")
      f.write("\n")
      f.write(f"{LABELS[i]}:\n")
      mean = round(np.mean(scores[-PROCESSING_RANGE_CLASSIFICATION:]), 3)
      standard_variation = round(np.std(scores[-PROCESSING_RANGE_CLASSIFICATION:]), 3)
      standard_error = round(standard_variation/(math.sqrt(PROCESSING_RANGE_CLASSIFICATION)), 3)
      print(f"Mean: {mean}, Standard Error: {standard_error}, Standard Variation: {standard_variation}")
      f.write(f"Mean: {mean}, Standard Error: {standard_error}, Standard Variation: {standard_variation}\n")
    else:
      print(f"{LABELS[i]}:")
      f.write("\n")
      f.write(f"{LABELS[i]}:\n")
      mean = round(np.mean(scores[-PROCESSING_RANGE_SEGMENTATION:]), 3)
      standard_variation = round(np.std(scores[-PROCESSING_RANGE_SEGMENTATION:]), 3)
      standard_error = round(standard_variation/(math.sqrt(PROCESSING_RANGE_SEGMENTATION)), 3)
      print(f"Mean: {mean}, Standard Error: {standard_error}, Standard Variation: {standard_variation}")
      f.write(f"Mean: {mean}, Standard Error: {standard_error}, Standard Variation: {standard_variation}\n")
    print("")
  f.close()

# file_path = "Final_Output/CRNet_HU_256/train_log"
# file_path = "Final_Output/CRNet_PNG_256/train_log"

# file_path = "Final_Output/XNet_PNG_256/train_log"
# file_path = "Final_Output/OriginalIncoNet_PNG_256/train_log"
# file_path = "Final_Output/XNet_HU_256/train_log"
# file_path = "Final_Output/OriginalIncoNet_HU_256/train_log"

# file_path = "Final_Output/XNet_CAP_HU_256/train_log"
# file_path = "Final_Output/XNet_CAP_PNG_256/train_log"

file_path = "Final_Output/XNet_512/train_log"

file_path = file_path.replace("Final_Output", "Model Results")
_, _, _, _, test_data_class, test_data_mask = parse_data (file_path)
out_file_path = file_path.replace("train_log", "train_result")
process_result(np.concatenate((test_data_class, test_data_mask), axis=1), out_file_path)