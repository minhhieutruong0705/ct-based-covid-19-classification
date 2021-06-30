# -*- coding: utf-8 -*-
"""Covid19_CRNet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ski7s1frnLZdxCpLAKVzZwlALQeTI1Ls
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict

class ConvPool(nn.Module):

  def __init__(self, in_channels, out_channels, is_batch_norm = False):
    super(ConvPool, self).__init__()
    self.layers = OrderedDict([
                               ('conv', nn.Conv2d(
                                   in_channels = in_channels,
                                   out_channels = out_channels,
                                   kernel_size = 7, 
                                   stride = 1,
                                   padding = 3
                               )),
                               ('norm', nn.BatchNorm2d(out_channels)),
                               ('relu', nn.ReLU(inplace=True)),
                               ('pool', nn.MaxPool2d(
                                   kernel_size = 3,
                                   stride = 2,
                               ))               
    ])
    if (not is_batch_norm):
      self.layers.pop('norm')
    
    self.conv = nn.Sequential(self.layers)
  
  def forward(self, x):
    return self.conv(x)

# test model architecture
if __name__ == "__main__":
  model = ConvPool(1, 1, True)
  print(model)

class CRNet(nn.Module):

  def __init__(self, img_dimwh, in_channels=3, downs_features=[32, 64, 128]):
    super(CRNet, self).__init__()
    self.downs_features = downs_features

    self.downs_layers = OrderedDict()
    for i, feature in enumerate(downs_features):
      self.downs_layers[f'convpool{i+1}'] = ConvPool(in_channels, feature, feature==32)
      in_channels = feature
    self.downs = nn.Sequential(self.downs_layers)

    self.bottom = nn.ModuleDict({
     'globavgpool' : nn.AvgPool2d(
        kernel_size = 2,
        stride = 2,
     ),
     'linear' : nn.Linear(self._cal_features__(img_dimwh) ** 2 * downs_features[-1], 2)   
    })

  def _cal_features__(self, img_dimwh):
    globavgpool_dimwh = img_dimwh
    for i in range(len(self.downs_features)):
      globavgpool_dimwh = int(globavgpool_dimwh / 2 - 0.5)
    globavgpool_dimwh = int(globavgpool_dimwh / 2)
    return globavgpool_dimwh


  def forward(self, x):
    x = self.downs(x)
    x = self.bottom['globavgpool'](x)
    x = torch.flatten(x, 1)
    return self.bottom['linear'](x)

# test model architecture
if __name__ == "__main__":
  model = CRNet(23)
  print(model)

# test CRNet
def test_CRNet():
    x = torch.randn((1, 3, 224, 224))
    model = CRNet(img_dimwh=224, in_channels=3)
    pred = model(x)
    output = F.log_softmax(pred, dim=1)
    print(pred.shape, output)

if __name__ == '__main__':
  test_CRNet()