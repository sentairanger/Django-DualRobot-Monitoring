from django.shortcuts import render, HttpResponseRedirect
import logging
from jaeger_client import Config
from os import getenv
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import OutputDevice, LED, Servo, PWMOutputDevice

# Define the jaeger host
JAEGER_HOST = getenv('JAEGER_HOST', 'localhost')

# Define the Jaeger client
def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
            'local_agent': {'reporting_host': JAEGER_HOST},
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

tracer = init_tracer('eye-service')

# Define the factories
factory = PiGPIOFactory(host='192.168.0.24')
factory2 = PiGPIOFactory(host='192.168.0.23')

# Define both robots
en_1 = PWMOutputDevice(12, pin_factory=factory)
en_2 = PWMOutputDevice(26, pin_factory=factory)
motor_in1 = OutputDevice(13,  pin_factory = factory)
motor_in2 = OutputDevice(21,  pin_factory = factory)
motor_in3 = OutputDevice(17,  pin_factory = factory)
motor_in4 = OutputDevice(27,  pin_factory = factory)

pin1 = OutputDevice(7,  pin_factory = factory2)
pin2 = OutputDevice(8,  pin_factory = factory2)
pin3 = OutputDevice(9,  pin_factory = factory2)
pin4 = OutputDevice(10,  pin_factory = factory2)

#Define the eyes
linus_eye = LED(16, pin_factory=factory)
torvalds_eye = LED(25, pin_factory=factory2)

#define the servos
servo1 = Servo(22, pin_factory=factory)
servo2 = Servo(23, pin_factory=factory)
# Create your views here.

def index(request):
    return render(request, 'dualrobotapp/dualrobot.html', {})

# Linus robot movement
def forward(request):
    motor_in1.on()
    motor_in2.off()
    motor_in3.on()
    motor_in4.off()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def backward(request):
    motor_in1.off()
    motor_in2.on()
    motor_in3.off()
    motor_in4.on()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def left(request):
    motor_in1.off()
    motor_in2.on()
    motor_in3.on()
    motor_in4.off()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def right(request):
    motor_in1.on()
    motor_in2.off()
    motor_in3.off()
    motor_in4.on()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def stop(request):
    motor_in1.off()
    motor_in2.off()
    motor_in3.off()
    motor_in4.off()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Torvalds robot movement
def north(request):
    pin1.off()
    pin2.on()
    pin3.on()
    pin4.off()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def south(request):
    pin1.on()
    pin2.off()
    pin3.off()
    pin4.on()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def west(request):
    pin1.on()
    pin2.off()
    pin3.on()
    pin4.off()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def east(request):
    pin1.off()
    pin2.on()
    pin3.off()
    pin4.on()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def stoptwo(request):
    pin1.off()
    pin2.off()
    pin3.off()
    pin4.off()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Servo movement

def servomin(request):
    servo1.min()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def servomid(request):
    servo1.mid()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def servomax(request):
    servo1.max()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def servomin2(request):
    servo2.min()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def servomid2(request):
    servo2.mid()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def servomax2(request):
    servo2.max()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Motor Speed control

def thirty(request):
    en_1.value = .3
    en_2.value = .3
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def fifty(request):
    en_1.value = .5
    en_2.value = .5
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def full(request):
    en_1.value = 1
    en_2.value = 1
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# eye blink control

def linuson(request):
    with tracer.start_span('linus-span') as span:
        linus_eye.on()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def linusoff(request):
    linus_eye.off()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def torvaldson(request):
    with tracer.start_span('torvalds-span') as span:
        torvalds_eye.on()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def torvaldsoff(request):
    torvalds_eye.off()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
