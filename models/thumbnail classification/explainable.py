import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.utils import save_image
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

from explainable_cnn import CNNExplainer
from matplotlib import pyplot as plt
import numpy as np

import cv2

# Local
from thumbnail_classification import Classifier

def normalize_array(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

def main() -> int:
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    img_size = 128, 128
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]),
        transforms.Resize(img_size),
    ])

    dataset = datasets.ImageFolder("./imgs/", transform = transform)
    class_dict = {idx:c for idx, c in enumerate(dataset.classes)}


    model = Classifier(
        device = device,
        image_size = (3, *img_size),
        n_classes = len(dataset.classes),
    )

    model.load_state_dict(torch.load("./model.pt"))

    img_name = "./imgs/1/5.png"
    img_class = "1"
    x_cnn = CNNExplainer(model, class_dict)
    saliency_map = x_cnn.get_saliency_map(
        img_name,
        img_class,
        img_size,
    )

    cpy = saliency_map.copy()
    cpy = (normalize_array(cpy) * 255.0).astype(np.uint8)
    cv2.imwrite("./saliency.jpg", cpy)

    return 0

if __name__ == '__main__':
    SystemExit(main())
