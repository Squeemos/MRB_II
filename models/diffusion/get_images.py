import torch
from torch.optim import AdamW
import torch.nn as nn
import torch.nn.functional as F

import numpy as np
import cv2
import yaml
import logging, os, time, sys
from tqdm import tqdm
import copy

from yt_utils import YouTubeCategories

from unet import UNetModel
from gaussian import GaussianDiffusion
from dataloading import load_images, create_dataloader, create_displayable_img, device_setup
from config import Config

def main() -> int:
    logging.basicConfig(level = os.environ.get("LOGLEVEL", "ERROR"))
    log = logging.getLogger(__name__)
    log.info("Loading config")
    config = Config("./diffusion_config.yaml")

    log.info("Setting up config")
    config.attention_resolutions = tuple([config.image_width // int(res) for res in config.attention_resolutions])
    config.channel_mult = tuple(config.channel_mult)
    config.model_channels = config.base_width
    config.lr = float(config.lr)
    config.num_classes = 14

    classes = ['1', '10', '15', '17', '19', '2', '20', '22', '23', '24', '25', '26', '27', '28']

    log.info("Setting up device")
    config.device = device_setup(config)

    log.info("Creating Diffusion")
    diffusion = GaussianDiffusion(config)

    log.info("Loading categories")
    cats = YouTubeCategories("https://squeemos.pythonanywhere.com/static/video_categories.json", local = False)

    log.info("Creating UNet")
    model = UNetModel(
        config.image_width,
        config.in_channels,
        config.model_channels,
        config.out_channels,
        config.num_res_blocks,
        config.attention_resolutions,
        config.time_emb_factor,
        config.dropout,
        config.channel_mult,
        config.conv_resample,
        config.dims,
        config.num_classes,
        config.use_checkpoint,
        config.use_fp16,
        config.num_heads,
        config.num_head_channels,
        config.num_heads_upsample,
        config.use_scale_shift_norm,
        config.resblock_updown,
        config.use_new_attention_order,
    ).to(config.device)

    model.load_state_dict(torch.load(f"{config.saved_model_name}.pt", map_location = config.device))

    params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    # print(f"{params:,}")

    counter = 0
    if not os.path.exists("./new_imgs/"):
        os.mkdir("./new_imgs")

    while True:
        for idx, cls in enumerate(classes):
            cls = int(cls)
            print(f"{cats.id_to_title[cls]:21}: {idx}")
        img_cls = int(input("What category of video thumbnail do you want to generate? "))
        if img_cls == -1:
            break
        img = diffusion.sample_one_image_with_class(model, img_cls, config)
        img = np.concatenate(img, axis=1)[:, :, ::-1]
        cv2.imwrite(f"./new_imgs/{counter:04}.png", img)
        counter += 1

    return 0


if __name__ == '__main__':
    SystemExit(main())
