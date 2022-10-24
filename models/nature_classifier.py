import torch
import torch.nn as nn
import torch.nn.functional as F

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
        convs = nn.Sequential(
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
        )

        # Calculate the output size
        fcn_layer_input = torch.zeros(size = (1, *img_size), requires_grad = False)
        n, output_size = convs(fcn_layer_input).shape

        # Fully connected classification
        self.network = nn.Sequential(
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
            nn.Linear(output_size, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, num_classes),
        )
        self.forward_grads = {}
        self.backward_grads = {}
        self.layer_names = {}

        for name, module in self.network.named_children():
            self.layer_names[module] = name
            module.register_forward_hook(self.forward_hook)
            module.register_full_backward_hook(self.backward_hook)

    def forward(self, input):
        return self.network(input)

    def classify(self, input):
        preds = F.softmax(self(input), dim = -1)
        _, preds = torch.max(preds, dim = -1)
        return preds

    def forward_hook(self, module_, input_, output_):
        self.forward_grads[self.layer_names[module_]] = output_

    def backward_hook(self, module_, grad_input_, grad_output_):
        self.backward_grads[self.layer_names[module_]] = grad_output_[0]
