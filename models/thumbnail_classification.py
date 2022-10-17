import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.utils import save_image
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

import numpy as np
from tqdm import tqdm
import sys

class Classifier(nn.Module):
    def __init__(self, device, *, image_size = None, n_classes = None, dataset = None):
        super(Classifier, self).__init__()

        self.device = device
        if image_size is not None and dataset is None:
            img_size = image_size
        elif image_size is None and dataset is not None:
            img_size = dataset[0][0].shape
        else:
            raise Exception("Either image size or dataset needs to be passed in")

        if n_classes is not None and dataset is None:
            num_classes = n_classes
        elif n_classes is None and dataset is not None:
            num_classes = len(dataset.classes)
        else:
            raise Exception("Either n_classes or dataset needs to be passed in")

        self.convs = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size = 3, padding = 1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size = 3, stride = 1, padding = 1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(64, 128, kernel_size = 3, stride = 1, padding = 1),
            nn.ReLU(),
            nn.Conv2d(128 ,128, kernel_size = 3, stride = 1, padding = 1),
            nn.ReLU(),
            nn.MaxPool2d(2,2),

            nn.Conv2d(128, 256, kernel_size = 3, stride = 1, padding = 1),
            nn.ReLU(),
            nn.Conv2d(256,256, kernel_size = 3, stride = 1, padding = 1),
            nn.ReLU(),
            nn.MaxPool2d(2,2),

            nn.Flatten(),
        ).to(device)

        fcn_layer_input = torch.zeros(size = (1, *img_size), requires_grad = False).to(device)
        n, output_size = self.convs(fcn_layer_input).shape

        self.mlp = nn.Sequential(
            nn.Linear(output_size, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, num_classes),
        )

    def forward(self, input):
        return self.mlp(self.convs(input))

def main():
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    # Hyper parameters
    batch_size = 8
    num_workers = 1
    pin_memory = False
    lr = 1e-5
    b1 = 0.5
    b2 = 0.99
    iterations = 3
    img_size = 128, 128

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]),
        transforms.Resize(img_size),
    ])
    dataset = datasets.ImageFolder("./imgs", transform = transform)

    train_size = int(len(dataset) * .8)
    test_size = len(dataset) - train_size

    train_imgs, test_imgs = random_split(dataset, [train_size, test_size])

    train_data_loader = DataLoader(
        train_imgs,
        batch_size = batch_size,
        shuffle = True,
        num_workers = num_workers,
        pin_memory = pin_memory,
    )
    test_data_loader = DataLoader(
        test_imgs,
        batch_size = batch_size,
        shuffle = False,
        num_workers = num_workers,
        pin_memory = pin_memory,
    )

    c = Classifier(
        device = device,
        dataset = dataset,
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(c.parameters(), lr = lr, betas = (b1, b2))

    c.train()
    for epoch in tqdm(range(iterations), position = 0, desc = "Epoch", leave = True, dynamic_ncols=True):
        batch_loss = 0
        for imgs, labels in train_data_loader:
            imgs, labels = imgs.to(device), labels.to(device)

            optimizer.zero_grad()

            outputs = c(imgs)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            batch_loss += loss.item()

        tqdm.write(f"Iteration: {epoch + 1:4}\tLoss: {batch_loss / len(train_data_loader):.4}")

if __name__ == '__main__':
    main()
