import os
import torch

config = dict()

config['INPUT_DIR'] = '/media/4TB/datasets/caltech/processed'
config['TRAIN_DIR'] = f"{config['INPUT_DIR']}/train"
config['VALID_DIR'] = f"{config['INPUT_DIR']}/val"

config['TRAIN_CSV'] = f"{config['INPUT_DIR']}/train.csv"
config['VALID_CSV'] = f"{config['INPUT_DIR']}/val.csv"

config['DEVICE'] = torch.device("cuda") if torch.cuda.is_available() else torch.device('cpu')

os.environ["LOGFILE"] = "output.log"
os.environ["LOGLEVEL"] = "INFO"

import numpy as np
import torch
from torch.utils.data import DataLoader
import torchvision
from AlexNet.model import AlexNetModel
# from AlexNet.properties import *
from common.dataset.dataset import ClassificationDataset
import pandas as pd
import matplotlib.pyplot as plt
from common.utils.logging_util import *
from common.utils.training_util import *
from AlexNet.transformation import *


class BaseExecutor(object):
    DEFAULTS = {
        'CHECKPOINT_PATH': ''
    }

    def __init__(self):
        self.__dict__.update(Executor.DEFAULTS, **config)


class Executor(BaseExecutor):
    def __init__(self, version, data_loader, config):
        super().__init__()
        self.version = version


e = Executor("", "", config=config)
