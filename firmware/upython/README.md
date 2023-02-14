## Micropython

[Pico micropython docs](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)

## Install upython

```
curl https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2 -o rp2-pico-latest.uf2
```

Reboot pico with BOOTSEL pressed, the ncopy the uf2 file

```
cp rp2-pico-latest.uf2 /path/to/rpi/filesystem
```

## Install host tools

```
pip install rshell mpremote
```

## Set up ssd1306 package

```
mpremote pip install ssd1306
```

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

## rshell

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
repl
import os
os.mkdir('/flash')
```

Copy script to /flash and run it

```
rshell
cp script.py /flash/ ; repl ~ import flash.script
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