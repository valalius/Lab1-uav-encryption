import cv2
import numpy as np
import random


def generate_permutation_table(num_blocks, seed):
    # Генерація таблиці перестановок за допомогою seed
    indices = list(range(num_blocks))
    rng = random.Random(seed)
    rng.shuffle(indices)
    return indices


def extract_blocks(img, grid_rows, grid_cols, block_h, block_w):
    # Розбиття зображення на блоки
    blocks = []
    for r in range(grid_rows):
        for c in range(grid_cols):
            block = img[
                r * block_h : (r + 1) * block_h, c * block_w : (c + 1) * block_w
            ]
            blocks.append(block)
    return blocks


def encrypt_image(image_path, grid_rows, grid_cols, seed):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Не вдалося завантажити зображення. Перевірте шлях.")

    h, w, _ = img.shape
    block_h = h // grid_rows
    block_w = w // grid_cols
    new_h = block_h * grid_rows
    new_w = block_w * grid_cols
    img = img[:new_h, :new_w]

    blocks = extract_blocks(img, grid_rows, grid_cols, block_h, block_w)

    num_blocks = grid_rows * grid_cols
    perm_table = generate_permutation_table(num_blocks, seed)

    encrypted_blocks = [None] * num_blocks
    for original_idx, new_idx in enumerate(perm_table):
        encrypted_blocks[new_idx] = blocks[original_idx]

    encrypted_img = np.zeros_like(img)
    for idx, block in enumerate(encrypted_blocks):
        r = idx // grid_cols
        c = idx % grid_cols
        encrypted_img[
            r * block_h : (r + 1) * block_h, c * block_w : (c + 1) * block_w
        ] = block

    return encrypted_img, perm_table, (block_h, block_w), (new_h, new_w)


def decrypt_image(
    enc_img, perm_table, grid_rows, grid_cols, block_dims, original_shape
):
    block_h, block_w = block_dims
    new_h, new_w = original_shape

    blocks = [None] * len(perm_table)
    encrypted_blocks = extract_blocks(enc_img, grid_rows, grid_cols, block_h, block_w)

    for original_idx, new_idx in enumerate(perm_table):
        blocks[original_idx] = encrypted_blocks[new_idx]

    decrypted_img = np.zeros((new_h, new_w, 3), dtype=np.uint8)
    for idx, block in enumerate(blocks):
        r = idx // grid_cols
        c = idx % grid_cols
        decrypted_img[
            r * block_h : (r + 1) * block_h, c * block_w : (c + 1) * block_w
        ] = block

    return decrypted_img


def main():
    grid_rows = 12
    grid_cols = 16
    seed = 44257

    input_path = "input.jpg"

    print("Шифрування зображення...")
    encrypted_img, perm_table, block_dims, orig_shape = encrypt_image(
        input_path, grid_rows, grid_cols, seed
    )
    cv2.imwrite("encrypted.jpg", encrypted_img)

    print("Дешифрування зображення...")
    dec_img = decrypt_image(
        encrypted_img, perm_table, grid_rows, grid_cols, block_dims, orig_shape
    )
    cv2.imwrite("decrypted.jpg", dec_img)

    print("Готово! Результати збережено як encrypted.jpg та decrypted.jpg")


if __name__ == "__main__":
    main()