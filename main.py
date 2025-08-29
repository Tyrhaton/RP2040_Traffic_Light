from machine import Pin, PWM
from time import ticks_ms, ticks_diff, sleep_ms

# ========= Settings =========
# GPIO mapping (adjust to your wiring)
PIN_CAR_GREEN   = 18
PIN_CAR_ORANGE  = 17
PIN_CAR_RED     = 16
PIN_PED_RED     = 19
PIN_PED_GREEN   = 20
PIN_BUTTON      = 15

# Brightness per light (in %) — adjust
BR_CAR_GREEN    = 1
BR_CAR_ORANGE   = 10
BR_CAR_RED      = 10
BR_PED_RED      = 10
BR_PED_GREEN    = 1   # pedestrian green at 1%

PWM_FREQ_HZ = 1000    # ~1 kHz, flicker-free

# Timings (in seconds) — adjust as desired
MIN_CAR_GREEN_S   = 1
CAR_ORANGE_S      = 2
ALL_RED_S         = 1
PED_GREEN_S       = 5
PED_GREEN_BLINK_S = 3    # set to 0 to disable blink phase

DEBOUNCE_MS = 200       # debounce for the button

# ========= LED helper =========
class LedPWM:
    def __init__(self, pin_nr, brightness_percent=10, freq=1000):
        self.pwm = PWM(Pin(pin_nr))
        self.pwm.freq(freq)
        self._level = 0
        self._is_on = False
        self.set_percent(brightness_percent)
        self.off()

    def set_percent(self, percent):
        # clamp 0..100
        percent = 0 if percent < 0 else (100 if percent > 100 else percent)
        self._level = int(percent * 65535 // 100)
        if self._is_on:
            self.pwm.duty_u16(self._level)

    def on(self):
        self.pwm.duty_u16(self._level)
        self._is_on = True

    def off(self):
        self.pwm.duty_u16(0)
        self._is_on = False

    def toggle(self):
        if self._is_on:
            self.off()
        else:
            self.on()

# ========= Hardware setup =========
carGreen   = LedPWM(PIN_CAR_GREEN,   BR_CAR_GREEN,   PWM_FREQ_HZ)
carOrange  = LedPWM(PIN_CAR_ORANGE,  BR_CAR_ORANGE,  PWM_FREQ_HZ)
carRed     = LedPWM(PIN_CAR_RED,     BR_CAR_RED,     PWM_FREQ_HZ)
pedRed     = LedPWM(PIN_PED_RED,     BR_PED_RED,     PWM_FREQ_HZ)
pedGreen   = LedPWM(PIN_PED_GREEN,   BR_PED_GREEN,   PWM_FREQ_HZ)

button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_DOWN)

# ========= Helper functions =========
def all_car_off():
    carGreen.off()
    carOrange.off()
    carRed.off()

def all_ped_off():
    pedGreen.off()
    pedRed.off()

def sleep_s(seconds):
    # sleep in smaller steps so the loop remains responsive if needed
    ms = int(seconds * 1000)
    end = ticks_ms() + ms
    while ticks_diff(end, ticks_ms()) > 0:
        sleep_ms(5)

def pedestrian_cycle():
    """
    Full pedestrian cycle:
    - car green off -> car orange -> car red
    - all-red
    - pedestrian green (with optional blinking)
    - pedestrian red
    - all-red
    - car green
    """
    # 1) End car phase
    carGreen.off()
    carOrange.on()
    sleep_s(CAR_ORANGE_S)
    carOrange.off()
    carRed.on()

    # 2) All-red
    pedRed.on()  # stays red during overlap
    sleep_s(ALL_RED_S)

    # 3) Pedestrian green
    pedRed.off()
    pedGreen.on()
    if PED_GREEN_BLINK_S > 0 and PED_GREEN_S > PED_GREEN_BLINK_S:
        # steady green for the first part
        sleep_s(PED_GREEN_S - PED_GREEN_BLINK_S)
        # blinking for the last part
        t_end = ticks_ms() + PED_GREEN_BLINK_S * 1000
        while ticks_diff(t_end, ticks_ms()) > 0:
            pedGreen.toggle()
            sleep_ms(300)  # blink rate
        pedGreen.off()
    else:
        # no blink phase
        sleep_s(PED_GREEN_S)
        pedGreen.off()

    # 4) Pedestrian red
    pedRed.on()

    # 5) All-red back to car
    sleep_s(ALL_RED_S)

    # 6) Give cars green again
    carRed.off()
    carGreen.on()

# ========= Initial state (idle) =========
all_ped_off()
pedRed.on()

all_car_off()
carGreen.on()

last_press_time = 0
last_car_green_start = ticks_ms()  # to enforce minimum car green time

def min_car_green_elapsed():
    return ticks_diff(ticks_ms(), last_car_green_start) >= int(MIN_CAR_GREEN_S * 1000)

# ========= Main loop =========

onBoard = Pin("LED", Pin.OUT)

# Zet de LED aan
onBoard.value(1)

request = False
last_btn = 0
while True:
    # Read button with edge detection + debounce
    now = ticks_ms()
    btn = button.value()
    if btn == 1 and last_btn == 0 and ticks_diff(now, last_press_time) > DEBOUNCE_MS:
        last_press_time = now
        request = True
    last_btn = btn

    # If request is active and minimum car green time has elapsed, run the cycle
    if request and min_car_green_elapsed():
        request = False
        pedestrian_cycle()
        # after cycle ends, reset car green timer
        last_car_green_start = ticks_ms()

    sleep_ms(10)

