import time

# GPIO pin number configuration
TRIG_PIN = 118  # GPIO pin number for trigger output
ECHO_PIN = 120  # GPIO pin number for echo input
PWM_CHIP_PATH = '/sys/class/pwm/pwmchip0/'
PWM_PIN = 2

# GPIO initialization and release functions
def gpio_setup(pin, direction):
    # Export GPIO
    with open('/sys/class/gpio/export', 'w') as export_file:
        export_file.write(str(pin))

    # Configure direction
    with open(f"/sys/class/gpio/gpio{pin}/direction", 'w') as f:
        f.write(direction)

def gpio_unexport(pin):
    # Unexport GPIO
    with open('/sys/class/gpio/unexport', 'w') as unexport_file:
        unexport_file.write(str(pin))

def gpio_write(pin, value):
    with open(f"/sys/class/gpio/gpio{pin}/value", 'w') as f:
        f.write(str(value))

def gpio_read(pin):
    with open(f"/sys/class/gpio/gpio{pin}/value", 'r') as f:
        return int(f.read())

# PWM control functions
def enable_pwm(pwm_pin):
    with open(PWM_CHIP_PATH + 'export', 'w') as export_file:
        export_file.write(str(pwm_pin))

def disable_pwm(pwm_pin):
    with open(PWM_CHIP_PATH + 'unexport', 'w') as unexport_file:
        unexport_file.write(str(pwm_pin))

def set_pwm_period(pwm_pin, period_ns):
    with open(PWM_CHIP_PATH + f'pwm{pwm_pin}/period', 'w') as period_file:
        period_file.write(str(period_ns))

def set_pwm_duty_cycle(pwm_pin, duty_cycle_ns):
    with open(PWM_CHIP_PATH + f'pwm{pwm_pin}/duty_cycle', 'w') as duty_cycle_file:
        duty_cycle_file.write(str(duty_cycle_ns))

def enable_pwm_output(pwm_pin):
    with open(PWM_CHIP_PATH + f'pwm{pwm_pin}/enable', 'w') as enable_file:
        enable_file.write('1')

def disable_pwm_output(pwm_pin):
    with open(PWM_CHIP_PATH + f'pwm{pwm_pin}/enable', 'w') as enable_file:
        enable_file.write('0')

def set_servo_angle(pwm_pin, angle):
    # Adjust the servo motor's period and duty cycle to match the angle
    period_ns = 20000000  # 20ms period (50Hz frequency)
    duty_cycle_ns = int(1000000 + angle * 1000000 / 180)  # Duty cycle moving between 0.5ms and 2.5ms

    set_pwm_period(pwm_pin, period_ns)
    set_pwm_duty_cycle(pwm_pin, duty_cycle_ns)
    enable_pwm_output(pwm_pin)

# Ultrasonic distance measurement function
def measure_distance():
    # Initialize ultrasound transmission time
    gpio_write(TRIG_PIN, 0)
    time.sleep(0.2)  # Wait to reset

    gpio_write(TRIG_PIN, 1)
    time.sleep(0.00001)  # Emit ultrasound for 10 microseconds
    gpio_write(TRIG_PIN, 0)

    # Timing the echo pulse
    while gpio_read(ECHO_PIN) == 0:
        pulse_start = time.time()

    while gpio_read(ECHO_PIN) == 1:
        pulse_end = time.time()
        
    pulse_duration = pulse_end - pulse_start

    # Calculate distance (speed of sound is 343m/s)
    distance = pulse_duration * 17150

    return distance

if __name__ == '__main__':
    try:
        enable_pwm(PWM_PIN)
        gpio_setup(TRIG_PIN, 'out')
        gpio_setup(ECHO_PIN, 'in')

        while True:
            distance = measure_distance()
            print(f"Distance: {distance:.2f} cm")

            if distance <= 50:  # If distance is less than or equal to 50cm
                # Rotate the motor
                for angle in range(0, 180, 60):
                    set_servo_angle(PWM_PIN, angle)
                    time.sleep(0.1)  # Change motor operation cycle to 0.1 seconds
            else:
                # Stop the motor
                set_servo_angle(PWM_PIN, 90)  # Set angle to 90 degrees

            time.sleep(0.1)  # Change distance measurement interval to 0.1 seconds

    except KeyboardInterrupt:
        set_servo_angle(PWM_PIN, 90)
        disable_pwm_output(PWM_PIN)
        disable_pwm(PWM_PIN)
        gpio_unexport(TRIG_PIN)
        gpio_unexport(ECHO_PIN)
        print("\nProgram stopped.")
