import random

def add_laplace_noise(value, epsilon=1.0):
    scale = 1.0 / epsilon
    noise = random.gauss(0, scale)  # approx Laplace
    return value + noise
