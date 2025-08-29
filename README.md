# Raspberry Pi Pico (RP2040) - Traffic Light System with Pedestrian Crossing

This project is a **traffic light simulation** using a Raspberry Pi Pico.  
It simulates a traffic light for cars and a pedestrian crossing with a push button.  
The LEDs are controlled via **PWM** to reduce brightness (e.g., car LEDs at 10%, pedestrian green at 1%).

---

## Hardware

- **Raspberry Pi Pico** running MicroPython  
- LEDs + series resistors (220 Ω – 1 kΩ, depending on brightness)  
- Breadboard + jumper wires  
- 1 push button (for pedestrian request)  

### Pin Mapping (default in code)

| Signal          | GPIO pin |
|-----------------|----------|
| Car green       | GP18     |
| Car orange      | GP17     |
| Car red         | GP16     |
| Pedestrian red  | GP19     |
| Pedestrian green| GP20     |
| Button          | GP15     |

---

## Process Flow

1. **Idle state**  
   - Cars: **green**  
   - Pedestrians: **red**

2. **Button pressed**  
   - A pedestrian request is registered.  
   - The request is only processed after the minimum car green time has elapsed.

3. **Closing the car phase**  
   - Car green → **off**  
   - Car orange → **on** (3 s)  
   - Car red → **on**

4. **All-red safety interval**  
   - All lights red for 1 s

5. **Pedestrian phase**  
   - Pedestrian red → **off**  
   - Pedestrian green → **on** (5 s total)  
   - Last 3 s pedestrian green blinks

6. **Return to cars**  
   - Pedestrian green → **off**, pedestrian red → **on**  
   - Another 1 s all-red  
   - Car red → **off**, car green → **on**  
   - System returns to idle

---

## PWM Brightness

Each LED has its own brightness setting (in percentages).  
You can change these values at the top of the code:

```python
BR_AUTO_GREEN   = 10
BR_AUTO_ORANGE  = 10
BR_AUTO_RED     = 10
BR_PED_RED      = 10
BR_PED_GREEN    = 1
```

When calling on(), the LED is not fully powered (100% duty cycle) but dimmed with PWM.
off() turns the LED completely off.

### Usage

Flash MicroPython onto the Pico (using Thonny).

Copy the code (main.py) to the Pico.

Build the circuit on a breadboard according to the pin mapping.

Start the Pico.

Default: cars green, pedestrians red.

Press the button to request pedestrian crossing.

The system runs through the full cycle and returns to idle afterwards.

### Schematic

```md
[GP16] ---[220Ω]---|>|--- GND    Car Red LED
[GP17] ---[220Ω]---|>|--- GND    Car Orange LED
[GP18] ---[220Ω]---|>|--- GND    Car Green LED

[GP19] ---[220Ω]---|>|--- GND    Pedestrian Red LED
[GP20] ---[220Ω]---|>|--- GND    Pedestrian Green LED

[GP15] ---- Button ---- 3V3      Pedestrian Request Button

```

### Legend

- `[GPxx]` = GPIO pin on the Pico  
- `[220Ω]` = series resistor (adjust to 220–1kΩ depending on brightness)  
- `|>|` = LED (arrow pointing to ground = cathode side)  
- Button one side to GP15, the other side to **3V3**; Pico internally uses `PULL_DOWN`, so GP15 is `LOW` by default and goes `HIGH` when pressed.  

*You can also switch the LEDS with the resistors. as long as they stay in the same serie it will work.*
