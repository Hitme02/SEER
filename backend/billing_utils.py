import numpy as np
import tenseal as ts

# BBMP/BESCOM slab billing function
def compute_bbmp_bill(units):
    total = 0
    if units <= 50:
        total += units * 4.15
    elif units <= 100:
        total += 50 * 4.15 + (units - 50) * 5.60
    elif units <= 200:
        total += 50 * 4.15 + 50 * 5.60 + (units - 100) * 7.15
    else:
        total += 50 * 4.15 + 50 * 5.60 + 100 * 7.15 + (units - 200) * 8.20
    return total

# CKKS encryption context setup
def get_ckks_context():
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.generate_galois_keys()
    context.global_scale = 2 ** 40
    return context

# Encrypt value
def encrypt_bill_value(context, value):
    return ts.ckks_vector(context, [value])

# Decrypt value
def decrypt_bill_value(encrypted_vector):
    return encrypted_vector.decrypt()[0]

# Apply Laplace noise
def add_laplace_noise(value, noise_level):
    noise_map = {"Low": 1.0, "Medium": 3.0, "High": 6.0}
    noise_scale = noise_map.get(noise_level, 3.0)
    noise = np.random.laplace(loc=0.0, scale=noise_scale)
    return value + noise, noise
