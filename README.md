# nice!nano iButton to Home Assistant (BTHome V2)

This project implements a low-power wireless iButton reader using a **nice!nano** (nRF52840) or compatible clone. It communicates with Home Assistant via the **BTHome V2** protocol over Bluetooth Low Energy (BLE).

## Features
- **iButton Integration:** Scans and identifies iButtons (DS1990A) and broadcasts the ID.
- **Ultra-Low Power:** Optimized for battery life (Deep Sleep < 5µA).
- **Configurable Feedback:** Switch between the onboard LED or an external status LED via a software toggle.
- **Smart Power Management:** The iButton reader is only powered during the active scan window.
- **High-Precision Battery Sensing:** - Optimized for high-impedance 1MΩ/1MΩ voltage dividers.
  - Uses SAADC dummy sampling and oversampling for stability.
  - Software calibration factor for system-level accuracy.

## Hardware Setup
### Pinout
| Function | nice!nano Pin | nRF52840 Pin | Description |
| :--- | :--- | :--- | :--- |
| **Wake-up** | P0.29 | 0.29 | Connected to iButton Data line |
| **1-Wire Data**| P0.31 | 0.31 | Dedicated 1-Wire bus pin |
| **VCC Control**| P0.13 | 0.13 | Powers the reader via MOSFET/Transistor |
| **Battery ADC**| P0.02 | 0.02 | Analog input for 1M/1M divider |
| **External LED**| P0.06 | 0.06 | Optional external status LED |

### External LED Wiring
If using an external LED on **P0.06**:
1. Connect **P0.06** to a **470Ω resistor**.
2. Connect the resistor to the **Anode** (long leg) of the LED.
3. Connect the **Cathode** (short leg) of the LED to **GND**.

## Configuration
Customize the behavior at the top of `code.py`:

```python
USE_EXTERNAL_LED = True  # Set to False to use the built-in nice!nano LED
SLEEP_TIME = 300         # Time between battery heartbeats (seconds)
CALIBRATION_FACTOR = 1.02 # Fine-tune battery voltage readings