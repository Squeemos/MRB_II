import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.utils import save_image
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

import cv2

def between_minusone_and_one(x):
    return (2.0 * x) - 1.0

def load_images(config):
    transform = transforms.Compose([
        transforms.Resize((config.image_height, config.image_width)),
        # transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Lambda(lambda x : (2.0 * x) - 1.0),
        # transforms.Lambda(between_minusone_and_one),
        # transforms.Normalize([config.T_MEAN, config.T_MEAN, config.T_MEAN], [config.T_STD, config.T_STD, config.T_STD])
    ])

    dataset = datasets.ImageFolder(config.img_path, transform = transform)

    return dataset

def create_dataloader(config, dataset):
    return DataLoader(dataset, batch_size = config.batch_size, shuffle = config.shuffle, pin_memory = config.pin_memory, num_workers = config.num_workers)

def create_displayable_img(img, img_size, config):
    sample = img.permute(1, 2, 0).cpu().numpy()
    sample = cv2.cvtColor(sample, cv2.COLOR_RGB2BGR)
    sample = cv2.resize(sample, (img_size, img_size))
    return (sample / 2.0) + 1.0
    # return sample * [config.T_STD, config.T_STD, config.T_STD] + [config.T_MEAN, config.T_MEAN, config.T_MEAN]

def device_setup(config):
    if config.device == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")
