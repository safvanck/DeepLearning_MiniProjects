import numpy as np
import cv2
from common.tf.dataset.dataset import *
from AlexNet_TF2.properties import *
from AlexNet_TF2.executor import *
import timeit

if __name__ == '__main__':
    fields = {'image': 'image', 'label': 'class'}

    train_dataset = get_dataset_from_tfrecord(train=True, batch_size=128, tf_files=f"{config['TRAIN_DIR']}.tfrecord")
    val_dataset = get_dataset_from_tfrecord(tf_files=f"{config['VALID_DIR']}.tfrecord")
    test_dataset = get_dataset_from_tfrecord(tf_files=f"{config['VALID_DIR']}.tfrecord", repeat=1)

    e = Executor("", {'TRAIN': train_dataset, 'VAL': val_dataset, 'TEST': test_dataset}, config=config)

    start = timeit.default_timer()
    e.train()
    rank1, rank5 = e.prediction()
    print(f'Rank 1 Accuracy {rank1}, Rank 5 Accuracy {rank5},')
    stop = timeit.default_timer()
    print(f'Training Time: {round((stop - start) / 60, 2)} Minutes')
