# rag/scraper.py — auto-scrape robotics knowledge into .txt files
# Run: python rag/scraper.py
# Install first: pip install requests beautifulsoup4

import os
import time
import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = r"E:\ai_engineering_robotics_assistant_architecture\knowledge"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (educational research bot)"
}

# ── Sources to scrape ─────────────────────────────────────────────
SOURCES = [

    # ARDUINO & ESP32
    {
        "filename": "arduino_servo_library.txt",
        "url": "https://www.arduino.cc/reference/en/libraries/servo/",
        "topic": "Arduino Servo Library"
    },
    {
        "filename": "arduino_pwm_analogwrite.txt",
        "url": "https://www.arduino.cc/reference/en/language/functions/analog-io/analogwrite/",
        "topic": "Arduino PWM analogWrite"
    },
    {
        "filename": "arduino_serial_debug.txt",
        "url": "https://www.arduino.cc/reference/en/language/functions/communication/serial/",
        "topic": "Arduino Serial Communication"
    },
    {
        "filename": "esp32_pinout_guide.txt",
        "url": "https://randomnerdtutorials.com/esp32-pinout-reference-gpios/",
        "topic": "ESP32 GPIO Pinout Reference"
    },
    {
        "filename": "esp32_wifi_basics.txt",
        "url": "https://randomnerdtutorials.com/esp32-useful-wi-fi-functions-arduino/",
        "topic": "ESP32 WiFi Functions"
    },

    # SERVO & STEPPER MOTORS
    {
        "filename": "servo_motor_troubleshooting.txt",
        "url": "https://www.robotshop.com/community/tutorials/show/servo-motor-tutorial",
        "topic": "Servo Motor Troubleshooting"
    },
    {
        "filename": "stepper_motor_basics.txt",
        "url": "https://lastminuteengineers.com/stepper-motor-l298n-arduino-tutorial/",
        "topic": "Stepper Motor with L298N"
    },
    {
        "filename": "stepper_a4988_driver.txt",
        "url": "https://lastminuteengineers.com/a4988-stepper-motor-driver-arduino-tutorial/",
        "topic": "A4988 Stepper Driver"
    },
    {
        "filename": "drv8825_stepper_driver.txt",
        "url": "https://lastminuteengineers.com/drv8825-stepper-motor-driver-arduino-tutorial/",
        "topic": "DRV8825 Stepper Driver"
    },

    # POWER ELECTRONICS & DRIVERS
    {
        "filename": "l298n_motor_driver.txt",
        "url": "https://lastminuteengineers.com/l298n-dc-stepper-driver-arduino-tutorial/",
        "topic": "L298N Motor Driver"
    },
    {
        "filename": "l293d_motor_driver.txt",
        "url": "https://lastminuteengineers.com/l293d-dc-motor-arduino-tutorial/",
        "topic": "L293D Motor Driver"
    },
    {
        "filename": "power_supply_robotics.txt",
        "url": "https://www.electronics-tutorials.ws/dccircuits/voltage-regulator.html",
        "topic": "Voltage Regulators for Robotics"
    },
    {
        "filename": "mosfet_motor_control.txt",
        "url": "https://www.electronics-tutorials.ws/transistor/tran_7.html",
        "topic": "MOSFET Motor Control"
    },

    # ROS / ROS2
    {
        "filename": "ros2_concepts_overview.txt",
        "url": "https://docs.ros.org/en/humble/Concepts/Basic.html",
        "topic": "ROS2 Basic Concepts"
    },
    {
        "filename": "ros2_nodes_topics.txt",
        "url": "https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html",
        "topic": "ROS2 Nodes and Topics"
    },
    {
        "filename": "ros2_publisher_subscriber.txt",
        "url": "https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html",
        "topic": "ROS2 Publisher Subscriber Python"
    },
]


def scrape(url: str, topic: str) -> str:
    """Fetch a page and extract clean text."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # remove nav, footer, scripts, ads
        for tag in soup(["script", "style", "nav", "footer",
                          "header", "aside", "form", "noscript"]):
            tag.decompose()

        # get main content — try common content containers first
        main = (soup.find("article") or
                soup.find("main") or
                soup.find(class_=["content", "main-content",
                                   "post-content", "entry-content"]) or
                soup.find("body"))

        if not main:
            return ""

        # extract paragraphs and headings as clean text
        lines = []
        for el in main.find_all(["h1", "h2", "h3", "h4", "p",
                                   "li", "pre", "code"]):
            text = el.get_text(separator=" ", strip=True)
            if len(text) < 20:   # skip very short fragments
                continue
            if el.name in ["h1", "h2", "h3", "h4"]:
                lines.append(f"\n{text.upper()}\n")
            else:
                lines.append(text)

        # join with blank lines between paragraphs (for chunking)
        content = f"TOPIC: {topic}\nSOURCE: {url}\n\n"
        content += "\n\n".join(lines)
        return content

    except Exception as e:
        print(f"  ERROR: {e}")
        return ""


def clean_text(text: str) -> str:
    """Remove excessive whitespace."""
    lines = [l.strip() for l in text.splitlines()]
    # collapse multiple blank lines into one
    cleaned, prev_blank = [], False
    for line in lines:
        is_blank = line == ""
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank
    return "\n".join(cleaned)


# ── Main scrape loop ──────────────────────────────────────────────
print(f"Scraping {len(SOURCES)} sources into {OUTPUT_DIR}\n")
success, failed = 0, 0

for source in SOURCES:
    print(f"  Scraping: {source['topic']}...")
    text = scrape(source["url"], source["topic"])

    if len(text) < 200:
        print(f"  SKIPPED — too little content ({len(text)} chars)")
        failed += 1
        continue

    text = clean_text(text)
    filepath = os.path.join(OUTPUT_DIR, source["filename"])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"  SAVED  — {len(text):,} chars → {source['filename']}")
    success += 1
    time.sleep(1.5)   # be polite — don't hammer servers

print(f"\nDone. {success} saved, {failed} skipped.")
print(f"Now run: python rag/build_vector_db.py")