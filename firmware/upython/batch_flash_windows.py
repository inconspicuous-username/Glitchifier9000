import os
import time
import argparse
import shutil
import traceback
import hashlib
import sys

import serial
import mpytool

UF2_FILE = "rp2-pico-latest.uf2"
BADGE_FILES_DIR = "badge"

RETRY_TIME = .5

parser = argparse.ArgumentParser()
parser.add_argument('RP2_WINDOWS_DISK', help='Expected RP2 bootloader windows disk letter')
parser.add_argument('RP2_WINDOWS_PORT', help='Expected RP2 USB COM port')
parser.add_argument('-v', '--verbose', action='count', default=0)
args = parser.parse_args()

RP2_WINDOWS_DISK = args.RP2_WINDOWS_DISK
RP2_WINDOWS_PORT = args.RP2_WINDOWS_PORT

try:
    import colorlog as logging
    logger = logging.getLogger(__name__)
    logging.basicConfig()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig()

logger.setLevel(logging.WARNING - args.verbose*10)
logger.debug('Very debug')

logger.debug('Building reference hash of badge files')
h = hashlib.sha256()
for f in os.listdir(BADGE_FILES_DIR):
    f2 = os.path.join(os.path.abspath(BADGE_FILES_DIR), os.path.basename(f))
    logger.debug(f'{f2=}')
    with open(f2, 'rb') as f2o:
        data = f2o.read()
        h.update(data)
ref_hash = h.digest()
logger.debug(f'{ref_hash.hex()=}')

print('Next badge please!')

while True:
    logger.debug('Start bootloader step')

    # Don't print error until this is 0
    disk_error_cnt = 20
    while True:
        try:
            x = os.listdir(f'{RP2_WINDOWS_DISK}:\\')
            if 'INDEX.HTM' not in x or 'INFO_UF2.TXT' not in x:
                logger.error(f'{RP2_WINDOWS_DISK=}:\\ did not contain expected files ({x})')
                time.sleep(RETRY_TIME)
                continue
            else:
                logger.debug(f'Found RP2 in boot mode')
        except FileNotFoundError as e:
            if disk_error_cnt < 0:
                logger.error(f'{RP2_WINDOWS_DISK=}:\\ not found')
                logger.error(f'Retrying from start of bootloader step in in {RETRY_TIME}s')
            else:
                disk_error_cnt -= 1
            time.sleep(RETRY_TIME)
            continue

        print('Badge detected!')

        logger.debug('Copying micropython uf2 file')
        try:
            shutil.copy(UF2_FILE, f'{RP2_WINDOWS_DISK}:\\')
            break
        except:
            logger.debug(traceback.format_exc())
            logger.error(f'Error copying {UF2_FILE=} to RP2')
            logger.error(f'Retrying from start of bootloader step in in {RETRY_TIME}s')
            time.sleep(RETRY_TIME)
            continue

    logger.info('Micropython UF2 programmed, wait for the serial port to show up')

    logger.debug(f'Waiting for {RP2_WINDOWS_PORT=} to show up')
    
    serial_error_cnt = 10
    while True:
        try:
            s = serial.Serial(RP2_WINDOWS_PORT, 115200)
            s.close()
            break
        except:
            if serial_error_cnt < 0:
                logger.debug(traceback.format_exc())
                logger.error(f'{RP2_WINDOWS_PORT=} not found')
                logger.error(f'Retry opening in {RETRY_TIME}s')
            else:
                serial_error_cnt -= 1
            time.sleep(RETRY_TIME)

    logger.debug('Open mpytool')
    conn = mpytool.ConnSerial(port=RP2_WINDOWS_PORT, baudrate=115200)
    mpy = mpytool.Mpy(conn)

    logger.debug('Copying badge firmware files')
    for f in os.listdir(BADGE_FILES_DIR):
        f2 = os.path.join(os.path.abspath(BADGE_FILES_DIR), os.path.basename(f))
        logger.debug(f'Putting {f2=}')
        with open(f2, 'rb') as f2o:
            data = f2o.read()
            mpy.put(data, f)

    logger.info('Badge firmware uploaded')

    logger.debug(f'Files in RP2: {mpy.ls()}')

    logger.debug('Verifying badge firmware files')
    h = hashlib.sha256()
    for f in os.listdir(BADGE_FILES_DIR):
        with open(f2, 'rb') as f2o:
            data = mpy.get(f)
            h.update(data)
    check_hash = h.digest()
    logger.debug(f'{check_hash.hex()=}')

    if check_hash != ref_hash:
        logger.error(f'Hash mismatch!')
        logger.error(f'  {ref_hash.hex()=}')
        logger.error(f'{check_hash.hex()=}')
        logger.error('Exit batch loop')
        break
    else:
        logger.info('Exit and reset, should see something on the screen')
        conn.write(b'\x02\x03\x04') 
    
    conn._serial.close()

    print('Next badge please!')
    while True:
        try:
            s = serial.Serial(RP2_WINDOWS_PORT, 115200)
            s.close()
            time.sleep(RETRY_TIME)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            break