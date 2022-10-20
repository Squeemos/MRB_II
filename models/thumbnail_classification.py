import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.utils import save_image
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

import numpy as np
from tqdm import tqdm
import sys, os

class Classifier(nn.Module):
    def __init__(self, device, *, image_size = None, n_classes = None):
        super(Classifier, self).__init__()

        # Device
        self.device = device

        # Size of the image
        if image_size is not None:
            img_size = image_size
        else:
            raise Exception("Please supply image size")

        # Number of classes
        if n_classes is not None:
            num_classes = n_classes
        else:
            raise Exception("Either n_classes or dataset needs to be passed in")

        # Nature cnn
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

        # Calculate the output size
        fcn_layer_input = torch.zeros(size = (1, *img_size), requires_grad = False).to(device)
        n, output_size = self.convs(fcn_layer_input).shape

        # Fully connected classification
        self.mlp = nn.Sequential(
            nn.Linear(output_size, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, num_classes),
        )
        self.grads = {}
        # 12
        # self.convs[12].register_forward_hook(self.forward_hook)
        # self.convs[12].register_full_backward_hook(self.backward_hook)

    def forward(self, input):
        output = self.mlp(self.convs(input))
        return output

    # #@staticmethod
    # def forward_hook(self, module, input, output):
    #     self.grads[saliency.base.CONVOLUTION_LAYER_VALUES] = torch.movedim(output, 1, 3).detach().cpu().numpy()
    #
    # def backward_hook(self, module, input, output):
    #     self.grads[saliency.base.CONVOLUTION_OUTPUT_GRADIENTS] = torch.movedim(output[0], 1, 3).detach().cpu().numpy()


def main():
    # Hyper parameters
    batch_size = 16
    num_workers = 1
    pin_memory = True
    lr = 1e-3
    b1 = 0.5
    b2 = 0.99
    iterations = 20
    img_size = 128, 128
    train_percentage = .8
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    # Transform the images on load (done lazily)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]),
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

    # Classifier
    c = Classifier(
        device = device,
        # dataset = dataset,
        image_size = (3, *img_size),
        n_classes = len(dataset.classes),
    ).to(device)

    # Setup loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(c.parameters(), lr = lr, betas = (b1, b2))

    # Set the model for training
    c.train()

    # Training
    for epoch in tqdm(range(iterations), desc = "Epoch", position = 0, leave = False):
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
            preds = c(imgs)
            preds = F.softmax(preds, dim = 1)
            _, preds = torch.max(preds, dim = 1)

            # Calculate totals
            total += labels.shape[0]
            n_correct += torch.sum(labels == preds).item()

        # Ending accuracy
        print(f"Testing Accuracy: {(n_correct / total) * 100:.2f}%")

    torch.save(c.state_dict(), "./model.pt")


if __name__ == '__main__':
    main()
