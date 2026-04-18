# nice!nano iButton to Home Assistant (BTHome V2)

This project implements a low-power wireless iButton reader using a **nice!nano** (nRF52840) or compatible clone. It communicates with Home Assistant via the **BTHome V2** protocol over Bluetooth Low Energy (BLE).

## Features
- **iButton Integration:** Scans and identifies iButtons (DS1990A) and broadcasts the ID.
- **Ultra-Low Power:** Optimized for battery life (Deep Sleep < 5µA).
- **Configurable Feedback:** Switch between the onboard LED or an external status LED via a software toggle.
- **Smart Power Management:** The iButton reader is only powered during the active scan window.
- **High-Precision Battery Sensing:** Optimized for high-impedance 1MΩ/1MΩ voltage dividers with software calibration.

## Hardware Setup
### Pinout
| Function | nice!nano Pin | nRF52840 Pin | Description |
| :--- | :--- | :--- | :--- |
| **Wake-up** | P0.29 | 0.29 | Connected to iButton Data line |
| **1-Wire Data**| P0.31 | 0.31 | Dedicated 1-Wire bus pin |
| **VCC Control**| P0.13 | 0.13 | Powers the reader via MOSFET/Transistor |
| **Battery ADC**| P0.02 | 0.02 | Analog input for 1M/1M divider |
| **External LED**| P0.06 | 0.06 | Optional external status LED |

### Battery Specification
- **Type:** 3.7V Lithium Polymer (LiPo) battery.
- **Connection:** Standard JST-PH 2.0mm connector (check polarity on your nice!nano clone!).
- **Voltage Range:** 3.4V (Empty) to 4.2V (Full).
- **Safety:** It is recommended to use a LiPo with an integrated protection circuit (PCM).

## Battery Life Expectancy (Conservative Estimate)
Based on a **1000mAh LiPo** battery and a 5-minute heartbeat interval:
- **Deep Sleep Current:** ~5-10µA.
- **Active Scan Current:** ~10mA (for approx. 1.5 seconds).
- **Expected Life:** **1.5 to 2.5 years** depending on the number of daily iButton scans and environmental factors (temperature). 
*Note: Using a high-efficiency external LED and keeping `SLEEP_TIME` at 300s or higher is key to achieving these results.*

## Software Installation
1. **Install CircuitPython:**
   - Download and install **CircuitPython 9.x** for the nice!nano from [circuitpython.org](https://circuitpython.org/board/nice_nano/).
2. **Download Libraries:**
   - Download the [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries).
   - Locate `adafruit_onewire` in the bundle and copy the entire folder to the `/lib` folder on your nice!nano.
3. **Deploy Code:**
   - Copy `code.py` from this repository to the root directory of your board.
4. **Configure:**
   - Adjust `USE_EXTERNAL_LED` and `SLEEP_TIME` in `code.py` as needed.

## Home Assistant Integration
The device is automatically discovered as a **BTHome** device. 
- **Sensor 0x01:** Battery Percentage.
- **Sensor 0x09:** iButton Tag ID (reports the last byte of the ROM).

## License
MIT License