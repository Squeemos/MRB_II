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

from unet import UNetModel
from gaussian import GaussianDiffusion
from dataloading import load_images, create_dataloader, create_displayable_img, device_setup
from config import Config

def main() -> int:
    logging.basicConfig(level = os.environ.get("LOGLEVEL", "INFO"))
    log = logging.getLogger(__name__)

    log.info("Loading config")
    config = Config("./diffusion_config.yaml")

    log.info("Setting up config")
    config.attention_resolutions = tuple([config.image_width // int(res) for res in config.attention_resolutions])
    config.channel_mult = tuple(config.channel_mult)
    config.model_channels = config.base_width
    config.lr = float(config.lr)

    log.info("Setting up device")
    config.device = device_setup(config)

    log.info("Loading dataset")
    dataset = load_images(config)

    log.info("Creating dataloader")
    dataloader = create_dataloader(config, dataset)
    config.num_classes = len(dataset.classes) if config.class_cond else None

    log.info("Creating Diffusion")
    diffusion = GaussianDiffusion(config)

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

    if config.use_trained:
        try:
            model.load_state_dict(torch.load(f"{config.saved_model_name}.pt"))
        except:
            log.info("Saved model not found, initializing from scratch...")

    config.ema_dict = copy.deepcopy(model.state_dict())

    log.info("Creating Optimizer")
    optimizer = AdamW(model.parameters(), lr = config.lr)

    log.info("Starting Training")
    for epoch in tqdm(range(config.epochs)):
        diffusion.train_one_epoch(dataloader, model, optimizer, config)

        if epoch % config.img_every == 0:
            sampled_images, labels = diffusion.sample_N_images(1, model, config)
            cv2.imwrite(
                f"{config.save_path}/{epoch:04}_{labels[0]}.png", np.concatenate(sampled_images, axis=1)[:, :, ::-1]
            )

        if epoch % config.save_every:
            torch.save(model.state_dict(), f"{config.saved_model_name}.pt")


    return 0

if __name__ == '__main__':
    SystemExit(main())
