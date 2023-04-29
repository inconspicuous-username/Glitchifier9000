## Micropython

[Pico micropython docs](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)

## Prepare upython environment

1. Reboot pico with BOOTSEL pressed, then copy the uf2 file to install upython
```
cp rp2-firmware/rp2-pico-latest.uf2 /path/to/rpi/filesystem
sync
```
Then wait until the device reboots to micropython ("Manufacturer: MicroPython" in dmesg).
2. Install host tools

```
pip install rshell mpremote
```
3. Set up ssd1306 package

```
mpremote mip install ssd1306
```

Potentially useful stuff
- https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html

- https://ssd1306.readthedocs.io/en/latest/python-usage.html

- [using PIL to convert image to monochrome image](https://github.com/adafruit/Adafruit_Python_SSD1306/blob/master/examples/image.py)

- [set GIMP to monochrome (1bit)](https://graphicdesign.stackexchange.com/questions/103717/how-do-i-create-true-two-color-images-in-gimp)

- https://docs.micropython.org/en/latest/library/framebuf.html

## Get vscode stubs:

[rp2 micropython stubs](https://github.com/Josverl/micropython-stubs)


Probably should do it in a venv:

```
python -m venv .venv
. .venv/bin/activate
pip install micropython-rp2-stubs
```

[set up for vscode](https://micropython-stubs.readthedocs.io/en/latest/22_vscode.html)

## Usage with mpytool (easier than rshell in some ways)

```
pip install mpytool
```

Open repl (doesn't work on windows):

```
mpytool -p /dev/tty*** repl
```

Upload folder:

```
mpytool -p /dev/tty*** put badge
```

Upload folder content:

```
mpytool -p /dev/tty*** put badge/
```

## Usage with rshell

Open [`rshell`](https://github.com/dhylands/rshell) (should detect your Pico automatically)

```
rshell
```

### Upload and run via rshell

Open a `repl`, use CTRL-X to drop back from the `repl` to `rshell`

```
repl
```

Create folder `/flash` on the rpi pico (once)

```
mkdir /pyboard/flash/
```

Copy script to /pyboard/flash and run it

```
cp script.py /pyboard/flash/ ; repl ~ import flash.script
```

### Run at boot

To run your script on power-up (instead of showing a `repl`), rename it to `/main.py`:

```
repl
import os
os.rename('/flash/script.py', '/main.py')
```

To have variables from `main.py`, you might have to reboot (CTRL-D).

# Connect OLED to I2C

For example: [oled](https://www.az-delivery.de/en/products/0-91-zoll-i2c-oled-display)

- Connect GND (pin 38 for example) with GND
- Connect VCC (pin 36, 3V3 out) with VCC
- Connect GP17 / I2C0 SCL (pin 22) with SCK
- Connect GP16 / I2C0 SDA (pin 21) with SDA

Can easily pick other pins for SCK/SDA