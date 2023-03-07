Set up PICO for badge

1. Set up micropython firmware

    - Boot RPI into bootloader mode (hold BOOTSEL button and plug in USB)
    - Copy micropython `uf2` file to storage device (download yourself or located in `firmware/upython/rp2-firmware/rp2-pico-latest.uf2`)

2. Copy firmware folder to device, for example with [`mpytool`](https://github.com/pavelrevak/mpytool)

    - `mpytool -p SERIALPORT put firmware/upython/badge/`

To do stuff over serial, connect with `SERIALPORT`, baudrate 115200.