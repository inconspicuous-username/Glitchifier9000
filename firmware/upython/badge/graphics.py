from debug import print_debug

OLED_WIDTH  = 128
OLED_HEIGHT = 64

OLED_I2C_ID = 0
OLED_I2C_SDA = 0
OLED_I2C_SCL = 1

print_debug(f'{OLED_WIDTH=}')
print_debug(f'{OLED_HEIGHT=}')
print_debug(f'{OLED_I2C_ID=}')
print_debug(f'{OLED_I2C_SDA=}')
print_debug(f'{OLED_I2C_SCL=}')

def rotate_row_bytes(buffer, rowidx, left):
    """Rotate all 8 bits of one row"""
    
    row_base = rowidx * OLED_WIDTH
    
    if left:
        first_byte = buffer[row_base]
        for idx in range(0, OLED_WIDTH-1):
            buffer[row_base + idx] = buffer[row_base + idx + 1]
        buffer[row_base + OLED_WIDTH-1] = first_byte

    else:
        first_byte = buffer[row_base + OLED_WIDTH-1]
        for idx in range(OLED_WIDTH-1, 0, -1):
            buffer[row_base + idx] = buffer[row_base + idx - 1]
        buffer[row_base] = first_byte