# Result Summary

## Structure

A training record consists of:
  - `train_log`
  - `graphs` directory: graphs of loss, accuracy, dice similarity coeficient, and F1 score on train, evaluation, and test sets
  - `train_result`: summarization of performance on **TEST** set

## Index Table
| Model | Dataset | Image Size | Folder |
| ----- | ------- | ---------- | ------ |
| **CRNet** | DICOM | 256x256 | [`CRNet_HU_256`](./CRNet_HU_256) |
| **CRNet** | PNG | 256x256 | [`CRNet_PNG_256`](./CRNet_PNG_256) |
| **CR-IM** | DICOM | 256x256 | [`OriginalIncoNet_HU_256`](./OriginalIncoNet_HU_256) |
| **CR-IM** | PNG | 256x256 | [`OriginalIncoNet_PNG_256`](./OriginalIncoNet_PNG_256) |
| **CR-IM-SCRE** | DICOM | 256x256 | [`XNet_HU_256`](./XNet_HU_256) |
| **CR-IM-SCRE** | PNG | 256x256 | [`XNet_PNG_256`](./XNet_PNG_256) |
| | | | |
| CR-IM-SCRE | DICOM - **CAP** | 256x256 | [`XNet_CAP_HU_256`](./XNet_CAP_HU_256) |
| CR-IM-SCRE | PNG - **CAP** | 256x256 | [`XNet_CAP_PNG_256`](./XNet_CAP_PNG_256) |
| | | | |
| CR-IM-SCRE | DICOM | **512x512** | [`XNet_512`](./XNet_512) |
