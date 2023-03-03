# Tools needed

`pip install mpytool`

# Upload micropython .uf2

Hold BOOTSEL button, plug in USB, copy paste `rp2-pico-latest.uf2`.

# Copy badge firmware

`mpytool -p PORT put buildcheck/` (the `/` at the end is important!)

Push some buttons, stuff should appear on the screen.
