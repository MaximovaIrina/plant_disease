import numpy as np
import torch
import cv2
import os


def features_labels(file, scale=False):
    dataset = torch.load(file)
    features = np.asarray(dataset['features'])
    if scale is True:
        features = (features - np.mean(features, axis=0)) / (np.std(features, axis=0) + 1e-9)
    labels = np.asarray(dataset['labels'])
    return features, labels


def scale(x, mean=None, std=None):
    if mean is None and std is None:
        mean, std = np.mean(x, 0), np.std(x, 0)
        return (x - mean) / std, mean, std
    else:
        return (x - mean) / std


def transform_features(x, length):
    x = x.copy()
    if length == 'long':
        return x
    elif length == 'middle':
        indices = list(range(8))
        for i in range(8, 68, 12):
            indices += list(range(i, i + 4))
        x = x[:, indices]
    elif length == 'short':
        indices = list(range(8))
        for i in range(8, 68, 12):
            ind = list(range(i, i + 4))
            x[:, i] = np.mean(x[:, ind], axis=1)
            indices += [i]
        x = x[:, indices]
    else:
        raise ValueError(f'Arg \'length\'={length} is not valid. Must be [\'long\', \'middle\', \'short\']')
    return x


def common_healthy_stat(root, path):
    file = os.path.join(os.getcwd(), path)
    if os.path.exists(file):
        data = torch.load(file)
    else:
        data_r = []
        data_ndvi = []
        files = os.listdir(os.path.join(os.getcwd(), root))
        for file in files:
            img = cv2.imread(os.path.join(root, file))
            ''' red '''
            red = img[:, :, 2]
            red_nz = red[red > 10]
            data_r += list(red_nz)
            ''' ndvi '''
            green = img[:, :, 1]
            ndvi = (green - red) / (green + red + 1e-9)
            ndvi[(red == 0) & (green == 0)] = 0
            ndvi = ndvi[(ndvi != 0) & (-0.95 < ndvi) & (ndvi < 0.95)]
            data_ndvi += list(ndvi)
        data = {'R_mean': np.mean(data_r), 'R_std': np.std(data_r),
                'ndvi_mean': np.mean(data_ndvi), 'ndvi_std': np.std(data_ndvi)}
    return data


def name_features():
    stat = ['MEAN', 'STD', 'MAX', 'MIN']
    hist = ['BIN_' + str(i) for i in range(4)]
    glcm = []
    for prop in ['CON', 'HOM', 'ENG', 'COR', 'ENT']:
        for d in [1, 4, 8]:
            for th in ['0', 'Pi/4', 'Pi/2', '3Pi/4']:
                glcm += [prop + '_' + str(d) + '_' + th]
    return np.concatenate([stat, hist, glcm])
