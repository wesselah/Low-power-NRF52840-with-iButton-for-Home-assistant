import time
import board
import digitalio
import analogio
import _bleio
import adafruit_onewire.bus
import gc
import supervisor 

# --- 1. CONFIGURATION ---
# >>> SETTINGS YOU CAN CHANGE <<<
USE_EXTERNAL_LED = True      # Set to True for P0.06, False for onboard LED
SLEEP_TIME = 300             # Deep sleep duration in seconds (5 minutes)
CALIBRATION_FACTOR = 1.02    # Battery voltage calibration
# >>> END OF SETTINGS <<<

WAKE_UP_PIN = board.P0_29    
ONEWIRE_PIN = board.P0_31    
VCC_CONTROL_PIN = board.P0_13 
VBAT_PIN = board.P0_02       
VOLT_MIN = 3.4             
VOLT_MAX = 4.18            

# --- LED SETUP ---
# Determine which pin to use based on the variable above
if USE_EXTERNAL_LED:
    target_led_pin = board.P0_06
    print("System: Using External LED (P0.06)")
else:
    target_led_pin = board.LED
    print("System: Using Onboard LED")

led = digitalio.DigitalInOut(target_led_pin)
led.direction = digitalio.Direction.OUTPUT
led.value = False 

# If using external LED, make sure the onboard one is explicitly OFF to save power
if USE_EXTERNAL_LED:
    onboard = digitalio.DigitalInOut(board.LED)
    onboard.direction = digitalio.Direction.OUTPUT
    onboard.value = False

def get_packet_count():
    return int(time.monotonic() * 100) % 255

def get_battery_voltage():
    adc = analogio.AnalogIn(VBAT_PIN)
    for _ in range(5):
        _ = adc.value
        time.sleep(0.01)
    raw_sum = 0
    for _ in range(10):
        raw_sum += adc.value
        time.sleep(0.005)
    adc.deinit()
    raw_avg = raw_sum / 10
    voltage = (raw_avg * 3.3 / 65535) * 2.0 * CALIBRATION_FACTOR
    return voltage

def get_battery_percentage(voltage):
    if voltage >= VOLT_MAX: return 100
    if voltage <= VOLT_MIN: return 0
    return int((voltage - VOLT_MIN) / (VOLT_MAX - VOLT_MIN) * 100)

def send_bthome_raw(payload_type, value):
    count = get_packet_count()
    full_payload = bytearray([0x08, 0x16, 0xD2, 0xFC, 0x40, 0x00, count, payload_type, value])
    try:
        _bleio.adapter.stop_advertising()
    except:
        pass
    _bleio.adapter.start_advertising(full_payload, connectable=False, interval=0.03)
    time.sleep(1.2) 
    _bleio.adapter.stop_advertising()

def scan_ibutton_standalone():
    tag_id = None
    vcc = digitalio.DigitalInOut(VCC_CONTROL_PIN)
    vcc.direction = digitalio.Direction.OUTPUT
    vcc.value = True 
    time.sleep(0.05) 
    try:
        with adafruit_onewire.bus.OneWireBus(ONEWIRE_PIN) as ow:
            devices = ow.scan()
            if devices:
                tag_id = devices[0].rom[-1]
    except:
        pass
    finally:
        vcc.value = False 
        vcc.deinit()
    return tag_id

# --- 2. EXECUTION LOGIC ---

if supervisor.runtime.serial_connected:
    # USB TEST MODE
    print(f"--- USB MODE: Testing Active (LED: {'External' if USE_EXTERNAL_LED else 'Onboard'}) ---")
    vcc_test = digitalio.DigitalInOut(VCC_CONTROL_PIN)
    vcc_test.direction = digitalio.Direction.OUTPUT
    vcc_test.value = True
    last_battery_send = 0
    
    try:
        test_bus = adafruit_onewire.bus.OneWireBus(ONEWIRE_PIN)
        while True:
            v_batt = get_battery_voltage()
            p_batt = get_battery_percentage(v_batt)
            print(f"Voltage: {v_batt:.2f}V | Percentage: {p_batt}%")
            
            if time.monotonic() - last_battery_send > 60:
                send_bthome_raw(0x01, p_batt)
                last_battery_send = time.monotonic()
                print(">> Battery status broadcasted to HA")

            devices = test_bus.scan()
            if devices:
                found = devices[0].rom[-1]
                print(f">> iButton found: {hex(found)}")
                led.value = True
                send_bthome_raw(0x09, found)
                time.sleep(0.4)
                send_bthome_raw(0x09, 0x00)
                led.value = False
            
            time.sleep(1.5)
            gc.collect()
            
    except Exception as e:
        print(f"USB Loop Error: {e}")
    finally:
        vcc_test.value = False
        vcc_test.deinit()

else:
    # BATTERY MODE (Deep Sleep)
    import alarm 
    
    tag_id = scan_ibutton_standalone()
    
    if tag_id:
        led.value = True
        send_bthome_raw(0x09, tag_id)
        time.sleep(0.4)
        send_bthome_raw(0x09, 0x00)
        led.value = False
    elif not isinstance(alarm.wake_alarm, alarm.pin.PinAlarm):
        v_batt = get_battery_voltage()
        p_batt = get_battery_percentage(v_batt)
        send_bthome_raw(0x01, p_batt)

    pin_a = alarm.pin.PinAlarm(pin=WAKE_UP_PIN, value=False, pull=True)
    time_a = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + SLEEP_TIME)
    
    alarm.exit_and_deep_sleep_until_alarms(pin_a, time_a)