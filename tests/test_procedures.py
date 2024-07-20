import cv2
import time
import random

from ili9341.ili9341_base import ILI9341_TFTWIDTH, ILI9341_TFTHEIGHT

TEST_RGB_COLORS = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "MAGENTA": (255, 0, 255),
    "CYAN": (0, 255, 255),
    "GRAY": (128, 128, 128),
}


def test_fullscreen_color_paint(lcd):
    print("Testing fullscreen color paints ...")
    for name, color in list(TEST_RGB_COLORS.items())[:4]:
        print("\tTesting {} ...".format(name))
        lcd.framebuff[:, :, :] = color
        lcd.update()
        time.sleep(1.5)


def test_draw_corner_boxes(lcd, size=100):
    print("Drawing colored boxes in the corners ... ")
    xmax = ILI9341_TFTWIDTH 
    ymax = ILI9341_TFTHEIGHT

    lcd.framebuff[:, :, :] = 0
    lcd.update()

    colors = ("RED", "GREEN", "BLUE", "YELLOW", "MAGENTA")
    boxes = (
        # x1, y1, x2, y2
        (0, 0, size, size), # top-left
        (xmax - size, 0, xmax, size), # top-right
        (xmax - size, ymax - size, xmax, ymax), # bot-right
        (0, ymax - size, size, ymax), # bot-left
        (int((xmax - size)/2), int((ymax - size)/2), int((xmax - size)/2 + size), int((ymax - size)/2 + size)) # center
    ) 

    for color, box in zip(colors, boxes):
        x1, y1, x2, y2 = box
        lcd.framebuff[y1:y2, x1:x2, :] = TEST_RGB_COLORS[color]
        lcd.update()
        time.sleep(0.1)


def test_display_image(lcd, path="baby_image.jpg"):
    print("Displaying image: {} ...".format(path))
    img = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)

    lcd.clear()
    lcd.framebuff[:, :, :] = img.swapaxes(0, 1)
    lcd.update()


def test_play_video(lcd, path="baby_video.mp4"):
    lcd.clear()

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError("Failed to open video!")

    while cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            break

        lcd.framebuff[:, :, :] = cv2.cvtColor(frame.swapaxes(0, 1), cv2.COLOR_BGR2RGB)
        lcd.update()


def test_webcam(lcd, webcam_index=0, fps=15, duration=10):
    lcd.clear()

    cap = cv2.VideoCapture(webcam_index)
    if not cap.isOpened():
        raise RuntimeError("Failed to open webcam!")

    n_frames = fps * duration
    i = 0
    while cap.isOpened() and i < n_frames:
        stime = time.time() 

        ret, frame = cap.read()
        frame = cv2.cvtColor(
            cv2.resize(frame, (ILI9341_TFTWIDTH, ILI9341_TFTHEIGHT)), cv2.COLOR_BGR2RGB)
        lcd.framebuff[:, :, :] = frame
        lcd.update()

        # Maintain FPS.
        etime = time.time()
        elapsed = etime - stime
        remaining = max(0.0, 1.0/fps - elapsed)
        time.sleep(remaining)

        i += 1


def test_draw_random_boxes(lcd, fps=60, duration=10, size=50):
    n_frames = fps * duration
    i = 0
    while i < n_frames:
        stime = time.time() 
        lcd.update()

        if i % 5 == 0:
            top = random.randint(0, ILI9341_TFTHEIGHT - size//2)
            left = random.randint(0, ILI9341_TFTWIDTH - size//2)
            bot = top + size
            right = left + size

        lcd.framebuff[top:bot, left:right, 0] = random.randint(0, 255)
        lcd.framebuff[top:bot, left:right, 1] = random.randint(0, 255)
        lcd.framebuff[top:bot, left:right, 2] = random.randint(0, 255)

        # Maintain FPS.
        etime = time.time()
        elapsed = etime - stime
        remaining = max(0.0, 1.0/fps - elapsed)
        time.sleep(remaining)

        i += 1


if __name__ == "__main__":
    lcd = MraaIli9341(
        spi_id=0,
        dcx_pin_id=3,
        rst_pin_id=5,
        spi_clock_hz=25000000,
        spi_data_chunk_size=2048)

    lcd.clear((0xFF, 0xFF, 0xFF))

    test_fullscreen_color_paint(lcd)
    time.sleep(1.0)
    test_draw_corner_boxes(lcd)
    time.sleep(1.0)
    test_draw_random_boxes(lcd)
    time.sleep(1.0)
    test_display_image(lcd)
    time.sleep(10.0)
    test_play_video(lcd)
    test_webcam(lcd)
