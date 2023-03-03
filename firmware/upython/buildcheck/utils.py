## No enum type in micropython
# https://github.com/micropython/micropython-lib/issues/269
def enum(**enums: int):
    return type('Enum', (), enums)
