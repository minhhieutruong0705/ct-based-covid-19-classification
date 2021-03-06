# -*- coding: utf-8 -*-
"""Covid19_Phase2_DatasetPreparation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1f1mSYl6AtPP0mPQPXN7Y3Y84dV_HiqM5
"""

from google.colab import drive
drive.mount('/content/drive', force_remount=True)

!pip install SimpleITK

import SimpleITK as sitk
import os
from tqdm import tqdm
import numpy as np
import glob2

WRITER = sitk.ImageFileWriter()
WRITER.KeepOriginalImageUIDOn()
def write_dicom(slide, slides_name, output_path, i):
  global WRITER
  file_name = f"{slides_name.split('.')[0]}_{i}.dcm"
  if os.path.isfile(os.path.join(output_path, file_name)):
    print('[INFO] Alert Filename Duplicated!____________________________________________')
  else:
    WRITER.SetFileName(os.path.join(output_path, file_name))
    WRITER.Execute(slide)

def load_nii_format_volume (input_path):
    file_name = os.path.basename(input_path)
    print("[INFO] Loading ", file_name)

    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    reader.SetFileName(input_path)
    slides = reader.Execute()

    print("[INFO] Volume Size: ", slides.GetSize())
    return slides, file_name

STATIC_IMAGE_FILTER = sitk.StatisticsImageFilter()
def is_black_mask(slide_mask):
  STATIC_IMAGE_FILTER.Execute(slide_mask)
  max_value = STATIC_IMAGE_FILTER.GetMaximum()
  if max_value > 0.0:
    return False
  else:
    return True

THRESHOLD_FILTER = sitk.ThresholdImageFilter()
THRESHOLD_FILTER.SetLower(0.0)
THRESHOLD_FILTER.SetLower(0.0)
THRESHOLD_FILTER.SetOutsideValue(1.0)
def normalize_mask(slide_mask):
  global THRESHOLD_FILTER
  slide_mask = THRESHOLD_FILTER.Execute(slide_mask)
  return slide_mask

def covid19_ct_lung_and_infection_segmentation(
    input_ct_dir='/content/drive/MyDrive/Dataset/COVID-19 CT Lung and Infection Segmentation/COVID-19-CT-Seg_20cases',
    input_lungmask_dir='/content/drive/MyDrive/Dataset/COVID-19 CT Lung and Infection Segmentation/Lung_Mask',
    input_lesionmask_dir='/content/drive/MyDrive/Dataset/COVID-19 CT Lung and Infection Segmentation/Infection_Mask',
    output_covid_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid',
    output_covid_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LungMask',
    output_covid_lesionmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LesionMask',
    output_normal_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal',
    output_normal_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal_LungMask'
):
  for filename in os.listdir(input_ct_dir):
    slides_ct, slides_ct_name = load_nii_format_volume(os.path.join(input_ct_dir, filename))
    slides_lungmask, slides_lungmask_name = load_nii_format_volume(os.path.join(input_lungmask_dir, filename))
    slides_lesionmask, slides_lesionmask_name = load_nii_format_volume(os.path.join(input_lesionmask_dir, filename))
    if (slides_ct.GetDepth() == slides_lungmask.GetDepth() and slides_ct.GetDepth() == slides_lesionmask.GetDepth()):
      print('[INFO] Valid Data:', slides_ct_name)
      print('[INFO] Normalizing Mask...')
      slides_lungmask = normalize_mask(slides_lungmask)
      slides_lesionmask = normalize_mask(slides_lesionmask)
      print('[INFO] Saving...')
      for i in tqdm(range(slides_ct.GetDepth())):
        if not is_black_mask(slides_lungmask[:,:,i]):
          if not is_black_mask(slides_lesionmask[:,:,i]):
            write_dicom(slides_ct[:,:,i], slides_ct_name, output_covid_ct_dir, i)
            write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_covid_lungmask_dir, i)
            write_dicom(slides_lesionmask[:,:,i], slides_ct_name, output_covid_lesionmask_dir, i)
          else:
            write_dicom(slides_ct[:,:,i], slides_ct_name, output_normal_ct_dir, i)
            write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_normal_lungmask_dir, i)
    else:
      print('[INFO] Invalid Data:', slides_ct_name)
      break

CAST_FILTER = sitk.CastImageFilter()
CAST_FILTER.SetOutputPixelType(sitk.sitkInt16)
def covid19_ct_segmentation_dataset(
    input_ct_file='/content/drive/MyDrive/Dataset/COVID-19 CT segmentation dataset/tr_im.nii.gz',
    input_lungmask_file='/content/drive/MyDrive/Dataset/COVID-19 CT segmentation dataset/tr_lungmasks_updated.nii.gz',
    input_lesionmask_file='/content/drive/MyDrive/Dataset/COVID-19 CT segmentation dataset/tr_mask.nii.gz',
    output_covid_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid',
    output_covid_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LungMask',
    output_covid_lesionmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LesionMask',
    output_normal_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal',
    output_normal_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal_LungMask'
):
  global CAST_FILTER
  slides_ct, slides_ct_name = load_nii_format_volume(input_ct_file)
  slides_lungmask, slides_lungmask_name = load_nii_format_volume(input_lungmask_file)
  slides_lesionmask, slides_lesionmask_name = load_nii_format_volume(input_lesionmask_file)
  if (slides_ct.GetDepth() == slides_lungmask.GetDepth() and slides_ct.GetDepth() == slides_lesionmask.GetDepth()):
    print('[INFO] Valid Data:', slides_ct_name)
    print('[INFO] Normalizing Mask...')
    slides_lungmask = normalize_mask(slides_lungmask)
    slides_lesionmask = normalize_mask(slides_lesionmask)
    print('[INFO] Casting to int16 ...')
    slides_ct = CAST_FILTER.Execute(slides_ct)
    slides_lungmask = CAST_FILTER.Execute(slides_lungmask)
    slides_lesionmask = CAST_FILTER.Execute(slides_lesionmask)
    print('[INFO] Saving...')
    for i in tqdm(range(slides_ct.GetDepth())):
      if not is_black_mask(slides_lungmask[:,:,i]):
        if not is_black_mask(slides_lesionmask[:,:,i]):
          write_dicom(slides_ct[:,:,i], slides_ct_name, output_covid_ct_dir, i)
          write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_covid_lungmask_dir, i)
          write_dicom(slides_lesionmask[:,:,i], slides_ct_name, output_covid_lesionmask_dir, i)
        else:
          write_dicom(slides_ct[:,:,i], slides_ct_name, output_normal_ct_dir, i)
          write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_normal_lungmask_dir, i)
  else:
    print('[INFO] Invalid Data:', slides_ct_name)

def radiopaedia(
    input_ct_dir='/content/drive/MyDrive/Dataset/Radiopaedia/rp_im',
    input_lungmask_dir='/content/drive/MyDrive/Dataset/Radiopaedia/rp_lung_msk',
    input_lesionmask_dir='/content/drive/MyDrive/Dataset/Radiopaedia/rp_msk',
    output_covid_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid',
    output_covid_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LungMask',
    output_covid_lesionmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LesionMask',
    output_normal_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal',
    output_normal_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal_LungMask'
):
  for filename in os.listdir(input_ct_dir):
    slides_ct, slides_ct_name = load_nii_format_volume(os.path.join(input_ct_dir, filename))
    slides_lungmask, slides_lungmask_name = load_nii_format_volume(os.path.join(input_lungmask_dir, filename))
    slides_lesionmask, slides_lesionmask_name = load_nii_format_volume(os.path.join(input_lesionmask_dir, filename))
    if (slides_ct.GetDepth() == slides_lungmask.GetDepth() and slides_ct.GetDepth() == slides_lesionmask.GetDepth()):
      print('[INFO] Valid Data:', slides_ct_name)
      print('[INFO] Normalizing Mask...')
      slides_lungmask = normalize_mask(slides_lungmask)
      slides_lesionmask = normalize_mask(slides_lesionmask)
      print('[INFO] Casting to int16 ...')
      slides_ct = CAST_FILTER.Execute(slides_ct)
      slides_lungmask = CAST_FILTER.Execute(slides_lungmask)
      slides_lesionmask = CAST_FILTER.Execute(slides_lesionmask)
      print('[INFO] Saving...')
      for i in tqdm(range(slides_ct.GetDepth())):
        if not is_black_mask(slides_lungmask[:,:,i]):
          if not is_black_mask(slides_lesionmask[:,:,i]):
            write_dicom(slides_ct[:,:,i], slides_ct_name, output_covid_ct_dir, i)
            write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_covid_lungmask_dir, i)
            write_dicom(slides_lesionmask[:,:,i], slides_ct_name, output_covid_lesionmask_dir, i)
          else:
            write_dicom(slides_ct[:,:,i], slides_ct_name, output_normal_ct_dir, i)
            write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_normal_lungmask_dir, i)
    else:
      print('[INFO] Invalid Data:', slides_ct_name)
      break

def covid_ct_md_normal(
    input_ct_dir='/content/drive/MyDrive/Dataset/COVID-CT-MD/NIfTI/Normal',
    input_lungmask_dir='/content/drive/MyDrive/Dataset/COVID-CT-MD/NIfTI/Normal_LungMask',
    output_normal_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal',
    output_normal_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal_LungMask'
):
  for filename in os.listdir(input_ct_dir):
    slides_ct, slides_ct_name = load_nii_format_volume(os.path.join(input_ct_dir, filename))
    slides_lungmask, slides_lungmask_name = load_nii_format_volume(os.path.join(input_lungmask_dir, filename.replace(".nii.gz", "_lungmask_.nii")))
    if (slides_ct.GetDepth() == slides_lungmask.GetDepth()):
      print('[INFO] Valid Data:', slides_ct_name)
      print('[INFO] Normalizing Mask...')
      slides_lungmask = normalize_mask(slides_lungmask)
      print('[INFO] Saving...')
      for i in tqdm(range(slides_ct.GetDepth())):
        if not is_black_mask(slides_lungmask[:,:,i]):
          write_dicom(slides_ct[:,:,i], slides_ct_name, output_normal_ct_dir, i)
          write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_normal_lungmask_dir, i)
    else:
      print('[INFO] Invalid Data:', slides_ct_name)
      break

def mosmed(
    input_ct_dir='/content/drive/MyDrive/Dataset/MosMed/CT-1',
    input_lungmask_dir='/content/drive/MyDrive/Dataset/MosMed/lung_masks',
    input_lesionmask_dir='/content/drive/MyDrive/Dataset/MosMed/masks',
    output_covid_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid',
    output_covid_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LungMask',
    output_covid_lesionmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LesionMask',
    output_normal_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal',
    output_normal_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal_LungMask'
):
  for filename in os.listdir(input_ct_dir):
    slides_ct, slides_ct_name = load_nii_format_volume(os.path.join(input_ct_dir, filename))
    slides_lungmask, slides_lungmask_name = load_nii_format_volume(os.path.join(input_lungmask_dir, filename.replace(".nii.gz", "_lungmask_.nii.gz")))
    slides_lesionmask, slides_lesionmask_name = load_nii_format_volume(os.path.join(input_lesionmask_dir, filename.replace(".nii.gz", "_mask.nii")))
    if (slides_ct.GetDepth() == slides_lungmask.GetDepth() and slides_ct.GetDepth() == slides_lesionmask.GetDepth()):
      print('[INFO] Valid Data:', slides_ct_name)
      print('[INFO] Normalizing Mask...')
      slides_lungmask = normalize_mask(slides_lungmask)
      slides_lesionmask = normalize_mask(slides_lesionmask)
      print('[INFO] Saving...')
      for i in tqdm(range(slides_ct.GetDepth())):
        if not is_black_mask(slides_lungmask[:,:,i]):
          if not is_black_mask(slides_lesionmask[:,:,i]):
            write_dicom(slides_ct[:,:,i], slides_ct_name, output_covid_ct_dir, i)
            write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_covid_lungmask_dir, i)
            write_dicom(slides_lesionmask[:,:,i], slides_ct_name, output_covid_lesionmask_dir, i)
          else:
            write_dicom(slides_ct[:,:,i], slides_ct_name, output_normal_ct_dir, i)
            write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_normal_lungmask_dir, i)
    else:
      print('[INFO] Invalid Data:', slides_ct_name)
      break

def covid_ct_md_cap(
    input_ct_dir='/content/drive/MyDrive/Dataset/COVID-CT-MD/NIfTI/CAP',
    input_lungmask_dir='/content/drive/MyDrive/Dataset/COVID-CT-MD/NIfTI/CAP_LungMask',
    output_normal_ct_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/CAP',
    output_normal_lungmask_dir='/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/CAP_LungMask'
):
  for filename in os.listdir(input_ct_dir):
    slides_ct, slides_ct_name = load_nii_format_volume(os.path.join(input_ct_dir, filename))
    slides_lungmask, slides_lungmask_name = load_nii_format_volume(os.path.join(input_lungmask_dir, filename.replace(".nii.gz", "_lungmask_.nii.gz")))
    if (slides_ct.GetDepth() == slides_lungmask.GetDepth()):
      print('[INFO] Valid Data:', slides_ct_name)
      print('[INFO] Normalizing Mask...')
      slides_lungmask = normalize_mask(slides_lungmask)
      print('[INFO] Saving...')
      for i in tqdm(range(slides_ct.GetDepth())):
        if not is_black_mask(slides_lungmask[:,:,i]):
          write_dicom(slides_ct[:,:,i], slides_ct_name, output_normal_ct_dir, i)
          write_dicom(slides_lungmask[:,:,i], slides_ct_name, output_normal_lungmask_dir, i)
    else:
      print('[INFO] Invalid Data:', slides_ct_name)
      break

# #copy to anywhere in code that a test should be saved
# file_name = f"test.nii.gz"
# WRITER.SetFileName(os.path.join("/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset", file_name))
# WRITER.Execute(slides_lesionmask)

# #main
# covid19_ct_lung_and_infection_segmentation()
# covid19_ct_segmentation_dataset()
# radiopaedia()
# covid_ct_md_normal()
# mosmed()
# covid_ct_md_cap()

# !ls -1 /content/drive/MyDrive/Colab\ Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal_LungMask | wc -l
# !ls -1 /content/drive/MyDrive/Colab\ Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LungMask | wc -l
# 12562 + 3100

datset_path = "/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset"
covid_data_path = "/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid"
normal_data_path = "/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal"
cap_data_path = "/content/drive/MyDrive/Colab Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/CAP"
def generate_train_validation_test_set():
  train_ratio = 0.65
  validation_ratio = 0.20
  test_ratio = 0.15

  images_covid = glob2.glob(os.path.join(covid_data_path, "*.dcm"))
  images_normal = glob2.glob(os.path.join(normal_data_path, "*.dcm"))
  images_cap = glob2.glob(os.path.join(cap_data_path, "*.dcm"))

  covid_length = len(images_covid)
  normal_length = len(images_normal)
  cap_length = len(images_cap)
  print(covid_length, normal_length, cap_length)

  images_HU_Covid = []
  images_HU_Normal = []
  for image in images_covid:
    if (os.path.basename(image)).split('_')[0] != "radiopaedia":
      images_HU_Covid.append(image)
  for image in images_normal:
    if (os.path.basename(image)).split('_')[0] != "radiopaedia":
      images_HU_Normal.append(image)

  covid_length = len(images_HU_Covid)
  normal_length = len(images_HU_Normal)
  print(covid_length, normal_length)
  images_covid = images_HU_Covid
  images_normal = images_HU_Normal

  covid_train_end_idx = int(covid_length * train_ratio) - 1 
  covid_validation_end_idx = int(covid_length * (train_ratio + validation_ratio)) - 1
  normal_train_end_idx = int(normal_length * train_ratio) - 1
  normal_validation_end_idx = int(normal_length * (train_ratio + validation_ratio)) - 1
  cap_train_end_idx = int(cap_length * train_ratio) - 1 
  cap_validation_end_idx = int(cap_length * (train_ratio + validation_ratio)) - 1

  np.random.shuffle(images_covid)
  np.random.shuffle(images_normal)
  np.random.shuffle(images_cap)

  # covid
  with open(os.path.join(datset_path, "covid_train.txt"), "w") as f:
    for line in images_covid[:covid_train_end_idx]:
      f.write(os.path.basename(line)+'\n')
  f.close() 

  with open(os.path.join(datset_path, "covid_validation.txt"), "w") as f:
    for line in images_covid[covid_train_end_idx:covid_validation_end_idx]:
      f.write(os.path.basename(line)+'\n')
  f.close() 

  with open(os.path.join(datset_path, "covid_test.txt"), "w") as f:
    for line in images_covid[covid_validation_end_idx:]:
      f.write(os.path.basename(line)+'\n')
  f.close() 

  # normal
  with open(os.path.join(datset_path, "normal_train.txt"), "w") as f:
    for line in images_normal[:covid_train_end_idx]:
      f.write(os.path.basename(line)+'\n')
  f.close() 

  with open(os.path.join(datset_path, "normal_validation.txt"), "w") as f:
    for line in images_normal[covid_train_end_idx:covid_validation_end_idx]:
      f.write(os.path.basename(line)+'\n')
  f.close() 

  with open(os.path.join(datset_path, "normal_test.txt"), "w") as f:
    for line in images_normal[covid_validation_end_idx:covid_length]:
      f.write(os.path.basename(line)+'\n')
  f.close() 

  # cap
  with open(os.path.join(datset_path, "cap_train.txt"), "w") as f:
    for line in images_cap[:covid_train_end_idx]:
      f.write(os.path.basename(line)+'\n')
  f.close() 

  with open(os.path.join(datset_path, "cap_validation.txt"), "w") as f:
    for line in images_cap[covid_train_end_idx:covid_validation_end_idx]:
      f.write(os.path.basename(line)+'\n')
  f.close() 

  with open(os.path.join(datset_path, "cap_test.txt"), "w") as f:
    for line in images_cap[covid_validation_end_idx:covid_length]:
      f.write(os.path.basename(line)+'\n')
  f.close()

# generate_train_validation_test_set()

# !rm /content/drive/MyDrive/Colab\ Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal_LungMask/*
# !rm /content/drive/MyDrive/Colab\ Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/NONCOVID/Normal/*
# !rm /content/drive/MyDrive/Colab\ Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LesionMask/*
# !rm /content/drive/MyDrive/Colab\ Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid_LungMask/*
# !rm /content/drive/MyDrive/Colab\ Notebooks/Covid19/Phase2_IncorporatingBinaryClassification/Dataset/COVID/Covid/*