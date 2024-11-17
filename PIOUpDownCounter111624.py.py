################################################################################################
# Lesson 95  4 LED binary counter with increment, decrement btns     lesson95a111624.py        #
# State Machine   Y register: counter   X register: btn states                                 #
# X states:  (00)-no btn press, (01)-increment btn,  (10)-decrement btn, (11)- both btn press  #
# Failed to implement reliable 'both' btns pressed, so is undefined                            #
################################################################################################

from machine import Pin
from rp2 import asm_pio, PIO, StateMachine

@asm_pio(out_init = (PIO.OUT_LOW, )*4, out_shiftdir = PIO.SHIFT_RIGHT)
def up_down_counter():
    set(y,0)                 # LED counter in y register
    label('read_data')
    in_(pins, 2)             # isr  (01): increment;  (10): decrement; (11):both btns pressed
    mov(x, isr)              # store btn values in x
    mov(isr, null)           # reset isr for future btn data
    jmp(not_x, 'read_data')  # wait for btn press other than (00)
    mov(osr,y)               # save counter
    set(y,0b01)              # mask for increment btn press
    jmp(x_not_y,'decrement') # if y==x, increment btn pressed, else decrement pressed (or both)
    wait(0,pin,0)            # wait for increment btn release; increment btn pressed
    mov(y,osr)               # restore counter to y
    mov(y, invert(y))        # add 1 to y (counter): invert(y), y_dec, then invert(y)
    jmp(y_dec,'next')
    label('next')
    mov(y, invert(y))        # y incremented by 1
    mov(pins,y)              # update LEDs with counter (y)
    jmp('read_data')         # get new btn data
    label('decrement')       # decrement or both btns pressed; undefined for both btns pressed
    mov(y,osr)               # get the saved counter
    jmp(y_dec,'continue')    # decrement counter 
    label('continue')
    wait(0,pin,1)            # wait for decrement btn release
    mov(pins,y)              # update LEDs with counter (y)
    jmp('read_data')         # get new btn data
      
pin14, pin15 = Pin(14, Pin.IN, Pin.PULL_DOWN), Pin(15, Pin.IN, Pin.PULL_DOWN) 
sm0=StateMachine(0, up_down_counter, freq = 2000, out_base = Pin(0), in_base = pin14)
sm0.active(1)
