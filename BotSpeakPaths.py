#motor definitions

motorpath = '/sys/class/tacho-motor/motor{}/'
mspeed = motorpath + 'duty_cycle_sp'
mrun = motorpath + 'run'

#LED definitions

ledpath = '/sys/class/leds/ev3:{}:{}/'
ledbright = ledpath +'brightness'
