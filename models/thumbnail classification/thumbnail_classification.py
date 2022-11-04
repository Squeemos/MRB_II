import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.utils import save_image
from torchvision import datasets, transforms
from torchvision import models as models
from torch.utils.data import DataLoader, random_split
from torch.utils.tensorboard import SummaryWriter

import numpy as np
from tqdm import tqdm
import sys, os

from nature_classifier import Classifier

def main() -> int:
    # Hyper parameters
    batch_size = 32
    num_workers = 8
    pin_memory = True
    lr = 1e-4
    iterations = 50
    img_size = 128, 128
    train_percentage = .8
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    # Transform the images on load (done lazily)
    transform = transforms.Compose([
        transforms.ToTensor(),
        #transforms.Normalize([0.5], [0.5]),
        transforms.Resize(img_size),
    ])

    # Dataset is the folder of images
    dataset = datasets.ImageFolder("./imgs", transform = transform)

    # Split sizes
    train_size = int(len(dataset) * train_percentage)
    test_size = len(dataset) - train_size

    # Randomly split the train and test images
    train_imgs, test_imgs = random_split(dataset, [train_size, test_size])

    # Train images
    train_data_loader = DataLoader(
        train_imgs,
        batch_size = batch_size,
        shuffle = True,
        num_workers = num_workers,
        pin_memory = pin_memory,
    )

    # Test images
    test_data_loader = DataLoader(
        test_imgs,
        batch_size = batch_size,
        shuffle = False,
        num_workers = num_workers,
        pin_memory = pin_memory,
    )

    # # Classifier
    # c = Classifier(
    #     device = device,
    #     # dataset = dataset,
    #     image_size = (3, *img_size),
    #     n_classes = len(dataset.classes),
    # ).to(device)

    c = models.vgg19(weights = None).to(device)

    # Setup loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(c.parameters(), lr = lr)

    # Set the model for training
    c.train()

    writer = SummaryWriter(comment = "VGG19")

    global_step = 0
    # Training
    for epoch in tqdm(range(iterations), desc = "Epoch", position = 0, leave = False):
        avg_loss = []
        # Iterate over batches
        for imgs, labels in tqdm(train_data_loader, desc = "Batch", position = 1, leave = False):
            # Move everything to the device
            imgs, labels = imgs.to(device), labels.to(device)

            # Zero gradients
            optimizer.zero_grad()

            # Classify and compute loss
            outputs = c(imgs)
            loss = criterion(outputs, labels)

            # Back propagate
            loss.backward()

            #c.gradient_storage()

            # Back propagate
            optimizer.step()

            avg_loss.append(loss.item())

            writer.add_scalar("Loss", loss.item(), global_step)
            global_step += 1

    writer.close()


    # Set the model for eval
    c.eval()

    with torch.no_grad():
        total = 0
        n_correct = 0
        # Iterate over testing date
        for imgs, labels in test_data_loader:
            # Move everything to the same device
            imgs, labels = imgs.to(device), labels.to(device)

            # Classify and compute from logits
            # preds = c.classify(imgs)
            preds = F.softmax(c(imgs), dim = -1)
            _, preds = torch.max(preds, dim = -1)

            # Calculate totals
            total += labels.shape[0]
            n_correct += torch.sum(labels == preds).item()

        # Ending accuracy
        print(f"Testing Accuracy: {(n_correct / total) * 100:.2f}%")

    torch.save(c.state_dict(), "./vgg19.pt")

    return 0


if __name__ == '__main__':
    SystemExit(main())
