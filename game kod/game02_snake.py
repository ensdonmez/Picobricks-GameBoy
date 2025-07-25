from machine import Pin, I2C
from sh1106 import SH1106_I2C
import time
import random

# OLED tanımı
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
oled = SH1106_I2C(128, 64, i2c)
oled.rotate(True)

# Butonlar
left = Pin(6, Pin.IN, Pin.PULL_UP)
right = Pin(9, Pin.IN, Pin.PULL_UP)
up = Pin(8, Pin.IN, Pin.PULL_UP)
down = Pin(7, Pin.IN, Pin.PULL_UP)
aButton = Pin(17, Pin.IN, Pin.PULL_UP)
bButton = Pin(16, Pin.IN, Pin.PULL_UP)
start = Pin(2, Pin.IN, Pin.PULL_UP)
select = Pin(3, Pin.IN, Pin.PULL_UP)

# LED ve Buzzer
redLED = Pin(20, Pin.OUT)
blueLED = Pin(19, Pin.OUT)
buzzer = Pin(18, Pin.OUT)

# Başlangıç
snake = [(64, 32), (60, 32)]  # 2 segment
direction = (4, 0)
food = (random.randint(0, 31) * 4, random.randint(0, 15) * 4)
score = 0

def draw():
    oled.fill(0)
    for segment in snake:
        oled.fill_rect(segment[0], segment[1], 4, 4, 1)
    oled.fill_rect(food[0], food[1], 4, 4, 1)
    oled.text("Score:" + str(score), 0, 0)
    oled.show()

def beep(duration=0.1):
    buzzer.value(1)
    time.sleep(duration)
    buzzer.value(0)

def game_over():
    redLED.value(1)
    oled.fill(0)
    oled.text("Game Over!", 30, 25)
    oled.text("Score: " + str(score), 30, 40)
    oled.show()

# Oyun döngüsü
last_input_time = time.ticks_ms()

while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, last_input_time) > 20:  # Buton tepki süresi hızlandırıldı
        if up.value() == 0 and direction != (0, 4):
            direction = (0, -4)
            last_input_time = now
        elif down.value() == 0 and direction != (0, -4):
            direction = (0, 4)
            last_input_time = now
        elif left.value() == 0 and direction != (4, 0):
            direction = (-4, 0)
            last_input_time = now
        elif right.value() == 0 and direction != (-4, 0):
            direction = (4, 0)
            last_input_time = now

    # Yeni baş hesapla
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # Kenar geçişi (wrap-around)
    x = head[0] % 128
    y = head[1] % 64
    head = (x, y)

    # Kendine çarptı mı?
    if head in snake:
        game_over()
        break

    # Yeni başı ekle
    snake.insert(0, head)

    # Yem yediyse
    if head == food:
        score += 1
        blueLED.value(1)
        beep(0.05)
        time.sleep(0.1)
        blueLED.value(0)
        # Yeni yem üret
        while True:
            new_food = (random.randint(0, 31) * 4, random.randint(0, 15) * 4)
            if new_food not in snake:
                food = new_food
                break
    else:
        snake.pop()  # Yem yenmedi, kuyruğu sil

    draw()
    time.sleep(0.15)  # Hızı belirler
