import tenseal as ts

def get_ckks_context(poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60], global_scale=2**40):
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=poly_modulus_degree,
        coeff_mod_bit_sizes=coeff_mod_bit_sizes,
    )
    context.generate_galois_keys()
    context.global_scale = global_scale
    return context

def encrypt_value(context, value):
    return ts.ckks_vector(context, [value])

def decrypt_value(context, encrypted_vector):
    return encrypted_vector.decrypt()[0]
