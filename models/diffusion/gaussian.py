import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

def unsqueeze3(x):
    return x[..., None, None, None]

class Scalars(object):
    def __init__(self, alpha_bar_scheduler, timesteps, device, betas = None):
        if betas is None:
            self.beta = torch.from_numpy(
                np.array([min(1 - alpha_bar_scheduler(t + 1) / alpha_bar_scheduler(t), 0.999) for t in range(timesteps)])).to(device)
        else:
            self.beta = betas

        self.beta_log = torch.log(self.beta).to(device)
        self.alpha = (1 - self.beta).to(device)
        self.alpha_bar = torch.cumprod(self.alpha, dim=0)
        self.beta_tilde = self.beta[1:] * (1 - self.alpha_bar[:-1]) / (1 - self.alpha_bar[1:])
        self.beta_tilde = torch.cat([self.beta_tilde[0:1], self.beta_tilde]).to(device)
        self.beta_tilde_log = torch.log(self.beta_tilde).to(device)

class GaussianDiffusion(object):
    def __init__(self, config):
        self.timesteps = config.timesteps
        self.device = config.device

        self.scalars = self.get_all_scalars()

    def alpha_bar_scheduler(self, t):
        return math.cos((t / self.timesteps + 0.008) / 1.008 * math.pi / 2) ** 2

    def clamp_x0(self, x):
        return x.clamp(-1, 1)

    def get_x0_from_xt_eps(self, xt, eps, t, scalars):
        return self.clamp_x0(1 / unsqueeze3(scalars.alpha_bar[t].sqrt()) * (xt - unsqueeze3((1 - scalars.alpha_bar[t]).sqrt()) * eps))

    def get_pred_mean_from_x0_xt(self, xt, x0, t, scalars):
        first = unsqueeze3((scalars.alpha_bar[t].sqrt() * scalars.beta[t]) / ((1 - scalars.alpha_bar[t]) * scalars.alpha[t].sqrt()))
        second = unsqueeze3((scalars.alpha[t] - scalars.alpha_bar[t]) / ((1 - scalars.alpha_bar[t]) * scalars.alpha[t].sqrt()))

        return first * x0 + second * xt

    def get_all_scalars(self, timesteps = None, betas = None):
        return Scalars(self.alpha_bar_scheduler, timesteps or self.timesteps, self.device, betas)

    def sample_from_forward_process(self, x0, t):
        eps = torch.randn_like(x0)
        xt = (
            unsqueeze3(self.scalars.alpha_bar[t].sqrt()) * x0
            + unsqueeze3((1 - self.scalars.alpha_bar[t]).sqrt()) * eps
        )
        return xt.float(), eps

    def sample_from_reverse_process(self, model, xT, timesteps = None, model_kwargs = {}, ddim = False):
        model.eval()
        final = xT
        timesteps = timesteps or self.timesteps
        new_timesteps = np.linspace(0, self.timesteps - 1, num = timesteps, endpoint = True, dtype = np.int)
        alpha_bar = self.scalars.alpha_bar[new_timesteps]
        new_betas = 1 - (alpha_bar / F.pad(alpha_bar, [1, 0], value = 1.0)[:-1])
        scalars = self.get_all_scalars(timesteps, new_betas)

        for i, t in zip(np.arange(timesteps)[::-1], new_timesteps[::-1]):
            with torch.no_grad():
                current_t = torch.tensor([t] * len(final), dtype = torch.long, device = final.device)
                current_sub_t = torch.tensor([i] * len(final), dtype = torch.long, device = final.device)
                pred_epsilon = model(final, current_t, **model_kwargs)
                pred_x0 = self.get_x0_from_xt_eps(final, pred_epsilon, current_sub_t, scalars)
                pred_mean = self.get_pred_mean_from_x0_xt(final, pred_x0, current_sub_t, scalars)
                if i == 0:
                    final = pred_mean
                else:
                    if ddim:
                        first = unsqueeze3(scalars.alpha_bar[current_sub_t - 1]).sqrt()
                        second = (1 - unsqueeze3(scalars.alpha_bar[current_sub_t - 1])).sqrt()
                        final = first * pred_x0 + second * pred_epsilon
                    else:
                        final = pred_mean + unsqueeze3(scalars.beta_tilde[current_sub_t].sqrt()) * torch.randn_like(final)
                final = final.detach()
                final = final.float()
        return final

    def train_one_epoch(self, dataloader, model, optimizer, config):
        model.train()
        for step, (images, labels) in enumerate(dataloader):
            images, labels = images.to(config.device), labels.to(config.device)
            t = torch.randint(self.timesteps, (len(images),), dtype = torch.int64).to(config.device)
            xt, eps = self.sample_from_forward_process(images, t)
            xt = xt.to(config.device)
            pred_eps = model(xt, t, y = labels if config.class_cond else None)

            loss = ((pred_eps - eps) ** 2).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # update ema_dict
            if config.local_rank == 0:
                new_dict = model.state_dict()
                for k, v in config.ema_dict.items():
                    config.ema_dict[k] = (config.ema_w * config.ema_dict[k] + (1 - config.ema_w) * new_dict[k])

    def sample_N_images(self, N, model, config, xT=None,):
        samples, labels, num_samples = [], [], 0
        while num_samples < N:
            if xT is None:
                xT = (
                    torch.randn(config.batch_size, config.num_channels, config.image_height, config.image_width, dtype = torch.float32)
                    .to(config.device)
                )
            if config.class_cond:
                y = torch.randint(config.num_classes, (len(xT),), dtype=torch.int64).to(
                    config.device
                )
            else:
                y = None
            gen_images = self.sample_from_reverse_process(
                model, xT, config.sampling_steps, {"y": y}, config.ddim
            )
            #samples_list = [torch.zeros_like(gen_images)]
            samples_list = [gen_images]
            if config.class_cond:
                #labels_list = [torch.zeros_like(y)]
                labels_list = [y]
                labels.append(torch.cat(labels_list).detach().cpu().numpy())

            samples.append(torch.cat(samples_list).detach().cpu().numpy())
            num_samples += len(xT)
        samples = np.concatenate(samples).transpose(0, 2, 3, 1)[:N]
        samples = (127.5 * (samples + 1)).astype(np.uint8)
        return samples, np.concatenate(labels)[:N] if config.class_cond else None
