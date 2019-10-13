import blynklib
import random
import blynktimer

colors = {'1': '#FFC300', '0': '#CCCCCC', 'OFFLINE': '#FF0000'}


BLYNK_AUTH = 'bTm3BTK7nTR2Bwk5kKSEt5uNtv5EjLjI'
blynk = blynklib.Blynk(BLYNK_AUTH)

"""
@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):
    blynk.virtual_write (3, '{}:{}:{}'.format(random.randint(0, 24), random.randint (0, 59), random.randint(0, 59)))
    blynk.virtual_write (2, random.randint(0, 1023))
    blynk.virtual_write (1, '{} C'.format(random.randint(10, 70)))
    blynk.virtual_write (0, random.uniform(0, 3.3))

@blynk.handle_event('write V5')
def write_handler (pin, value):
    button_state = value[0]
    blynk.set_property(pin, 'color', colors[button_state])    
"""

timer = blynktimer.Timer()
WRITE_EVENT_PRINT_MSG = "[WRITE_VIRTUAL_WRITE] Pin: V{} Value: '{}'"

@timer.register(vpin_num=8, interval=4, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = random.randint(0, 20)
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)


while True:
    blynk.run()