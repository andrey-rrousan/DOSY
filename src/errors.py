import matplotlib.pyplot as plt
import numpy as np

from src.mixture_fit import sum_exp_curv, fit


def bootstrap_resudial(n, x, y, bs_iters, bs_method='residuals', method='BFGS', seed=42, reg=0.0):
    np.random.seed(seed)
    init_theta = fit(x, y, n, method, reg)
    y_pred = sum_exp_curv(x, *init_theta)
    residuals = y_pred - y
    thetas_bs = np.zeros((bs_iters, len(init_theta)))
    for i in range(bs_iters):
        if bs_method == 'residuals':
            res_bs = np.random.choice(residuals, size=len(x))
            y_bs = y_pred + res_bs
        elif bs_method == 'wild':
            v = np.random.normal(0, 1, len(x))
            y_bs = y_pred + v * residuals
        else:
            raise ValueError('bs_method should be residuals or wild')
        y_bs[y_bs < 0] = -y_bs[y_bs < 0] * 0.5
        theta_i = fit(x, y_bs, n, method, reg)
        thetas_bs[i] = theta_i
    return init_theta, thetas_bs, residuals


def plot_parameters_space(thetas, bins=30, cut=0.0):
    fig, ax = plt.subplots(thetas.shape[1], thetas.shape[1], figsize=(15, 15))
    for i in range(thetas.shape[1]):
        for j in range(thetas.shape[1]):
            qs = np.quantile(thetas[:, i], [cut, 1 - cut])
            theta_i = thetas[:, i][(qs[0] <= thetas[:, i]) & (thetas[:, i] <= qs[1])]
            if i == j:
                ax[i, j].hist(theta_i, bins=bins)
            else:
                qs = np.quantile(thetas[:, j], [cut, 1 - cut])
                theta_j = thetas[:, j][(qs[0] <= thetas[:, j]) & (thetas[:, j] <= qs[1])]
                ax[i, j].hist2d(theta_j, theta_i, bins=bins)
            if j % 2 == 0:
                plt.setp(ax[-1, j], xlabel=f'w{j + 1 - j // 2}')
            else:
                plt.setp(ax[-1, j], xlabel=f'D{j - j // 2}')
        if i % 2 == 0:
            plt.setp(ax[i, 0], ylabel=f'w{i + 1 - i // 2}')
        else:
            plt.setp(ax[i, 0], ylabel=f'D{i - i // 2}')


def plot_errors(x, y, theta, res):
    plt.subplot(121)
    plt.plot(x, y, '.', label='data')
    plt.plot(x, sum_exp_curv(x, *theta), label='fit')
    plt.ylabel('$I/I_0$')
    plt.xlabel('Z * 1e-6')
    plt.legend()
    plt.subplot(122)
    plt.plot(x, res, '.')
    plt.xlabel('Z * 1e-6')
    plt.ylabel('residuals')
