#!/usr/bin/env python

import socket,struct,sys

def write(addr,value):
    'Writes a 16bit value to the Fusion part through the Xport.'
    request=struct.pack('<5B',0x02,addr&0xff,(addr&0xff00)>>8,value&0xff,(value&0xff00)>>8)
    xport.send(request)
    raw=xport.recv(10)
    if len(raw) != 1:
        print 'Received an invalid response. Received %i bytes:'%len(raw),raw_unpacked
        xport.close()
        sys.exit(1)

def read(addr):
    'Reads a 16bit value from the Fusion part through the Xport.'
    request=struct.pack('<3B',0x01,addr&0xff,(addr&0xff00)>>8)
    xport.send(request)
    raw=xport.recv(10)
    if len(raw) == 3:
        raw_unpacked=struct.unpack('<%iB'%len(raw),raw)
        #print 'Received: ',raw_unpacked
        value=(raw_unpacked[2]<<8) + raw_unpacked[1]
        #print 'Received value: ',value
        return value
    else:
        print 'Received an invalid response. Received %i bytes:'%len(raw),raw_unpacked
        xport.close()
        sys.exit(1)

def print_details():
    print '\nSerial number: %c%c%c%c%c%c.'%(chr(read(0xB8)),chr(read(0xB9)),chr(read(0xBA)),chr(read(0xBB)),chr(read(0xBC)),chr(read(0xBD)))
    print 'ID: %i, revision %i.%i.%i'%(read(0),read(1),read(2),read(3))
    print 'Board time: %i seconds'%((read(0x06)<<32)+(read(0x07)<<16)+(read(0x08)))

    pwr_state_raw=read(0x280)
    pwr_state=pwr_state_raw&7
    shutdown_reason=(pwr_state_raw&0x300)>>8
    print '\nPower state: %i (%s)'%(pwr_state,pwr_state_decode[pwr_state])
    print 'Reason for last shutdown: %i (%s)'%(shutdown_reason,shutdown_reason_decode[shutdown_reason])

    crashes=read(0x283)
    print '\nUnacknowledged crashes: %i'%crashes
    watchdog_overflows=read(0x284)
    print 'Unacknowledged watchdog overflows: %i'%watchdog_overflows
    print 'Watchdog timeout: %4.2f seconds.'%(read(0x285)*53.7)
    if crashes>0:
        #print 'Hard violation src %i val %i.'%(read(0x204),read(0x205))
        id=read(0x400)
        if id != 0xdead:
            print 'Crash ID fail: %x instead of 0xdead'%id
        else:
            time=((read(0x401)<<32)+(read(0x402)<<16)+(read(0x403)))
            src=read(0x404)
            val=read(0x405)
            print 'Flash crashlog: Crash at %is system time caused by channel %i (%s) with value %2.2f'%(time,src,channels[src],val/channel_scale[src])

    sys_config=read(0xffff)
    print '\nPPC bootstrap option H (boot from I2C EEPROM) is currently',
    if (sys_config&0x02): print 'ENABLED.'
    else: print 'DISABLED.'

    print 'Automatic safety shutdowns are currently',
    if (sys_config&0x80): print 'DISABLED.'
    else: print 'ENABLED.'

    if (sys_config&0x01): print 'ROACH will automatically power-up after reset.'
    else: print 'ROACH will remain powered-down after cold reset.'

    print '\nPower good from onboard voltage regulators:'
    ps_powergds=read(0x288)
    print '3v3aux: ',(ps_powergds&0x01)>>0
    print 'MGT_AVCCPLL: ',(ps_powergds&0x02)>>1
    print 'MGT_AVTTX: ',(ps_powergds&0x04)>>2
    print 'MGT_AVCC: ',(ps_powergds&0x08)>>3
    print 'ATX_PWR: ',(ps_powergds&0x10)>>4

    print 'ADC values are averaged %i times.'%(2**(read(0x145)))

    print '\nCurrent values:'
    print '%s \t%s \t%s \t%s'%('Channel'.rjust(17),'Current'.rjust(10), 'Shutdown'.rjust(10), 'Shutdown'.rjust(10))
    print '%s \t%s \t%s \t%s'%('Name'.rjust(15),'value'.rjust(8), 'below'.rjust(8), 'above'.rjust(8))
    print '====================================================================='
    for chan in valid_channels:
        sample_addr=0x240+chan
        hard_thresh_min_addr=0x1c0+(chan*2)
        hard_thresh_max_addr=0x1c0+(chan*2)+1
        
        sample=read(sample_addr)/channel_scale[chan] + channel_offset[chan]
        hard_thresh_min=read(hard_thresh_min_addr)/channel_scale[chan] + channel_offset[chan]
        hard_thresh_max=read(hard_thresh_max_addr)/channel_scale[chan] + channel_offset[chan]
        print '%s:\t %7.2f \t%7.2f \t%7.2f'%(channels[chan].rjust(15),sample,hard_thresh_min,hard_thresh_max)
    print '%s: \t%5i rpm'%('Fan 1'.rjust(15),read(0x300)*60)
    print '%s: \t%5i rpm'%('Fan 2'.rjust(15),read(0x301)*60)
    print '%s: \t%5i rpm'%('Fan 3'.rjust(15),read(0x302)*60)

def power_up():
    write(0x281,0xffff)

def warm_rst():
    write(0x282,0x0)

def power_down():
    write(0x282,0xffff)

def clear_crashlog():
    write(0x283,0xffff)

def toggle_config_h():
    print 'Retrieval of PPC bootstrap options from EEPROM (boot configuration H) is currently',
    sys_config=read(0xffff)
    if (sys_config&0x02):
        print 'enabled. DISABLING...',
        write(0xffff,sys_config-0x02)
        read(0x1000)
        if not read(0xffff)&0x2: 
            print 'done.'
            print 'PPC will now boot into configuration C (533MHz CPU, 66MHz bus) if all CONFIG_DIP switches are in OFF position.',
        else: print 'error saving.'
    else:
        print 'disabled. ENABLING...',
        write(0xffff,sys_config+0x02)
        read(0x1000)
        if read(0xffff)&0x2: 
            print 'done.'
            print 'PPC will now retrieve bootstrap options from EEPROM (bootstrap config H) if all CONFIG_DIP switches are in OFF position.',
        else: print 'error saving.'
        
def toggle_power_on_reset():
    print 'Automatic power-up after reset is currently',
    sys_config=read(0xffff)
    if (sys_config&0x01):
        print 'enabled. DISABLING...',
        write(0xffff,sys_config-0x01)
        read(0x1000)
        if not read(0xffff)&0x1: 
            print 'done.'
            print 'When Actel Fusion is hard-reset (cold reboot), ROACH will stay powered-off until commanded to power-up.'
        else: print 'error saving.'
    else:
        print 'disabled. ENABLING...',
        write(0xffff,sys_config+0x01)
        read(0x1000)
        if read(0xffff)&0x1: 
            print 'done.'
            print 'When Actel Fusion is hard-reset (cold reboot), it will automatically power-on ROACH immediately.' 
        else: print 'error saving.'

def toggle_hard_threshold():
    #SYSCTRL register value is retrieved from flash at 0xffff.
    #Commit writes to flash by following each write by a read to a different addr.
    
    #SYSCTRL bitmask:   bit0: Autostart on AC restore.
    #                   bit1: Enable EEPROM booting.
    #                   bit2:
    #                   bit3:
    #                   bit4:
    #                   bit5:
    #                   bit6:
    #                   bit7: Disable crashes (auto-shutdown in the event of bad power / over temp).
    #                   bit8:
    #                   bit9:
    #                   bit10:

    sys_config=read(0xffff)
    print '\nAutomatic safety shutdowns are currently',
    if (sys_config&0x80):
        print 'DISABLED. Enabling...',
        write(0xffff,sys_config-0x80)
        read(0x1000)
        if not read(0xffff)&0x80: print 'done.'
        else: print 'error saving.'
    else:
        print 'ENABLED. Disabling...',
        write(0xffff,sys_config+0x80)
        read(0x1000)
        if (read(0xffff)&0x80): 
            print 'done.\n\n'
            print '============================================================================'
            print '||  WARNING: Defeating the safety shutdowns could cause permanent damage  ||'
            print '||           to your board in the event of a fault.                       ||'
            print '============================================================================\n\n'
        else: print 'error saving.'
        


#START MAIN PROGRAM
xport_ip='192.168.4.20'
exit=False
channels={  7: '12V ATX (volts)', \
            10:'5V  ATX (volts)', \
            13:'3v3 ATX (volts)', \
            28:'2V5 PS  (volts)', \
            25:'1V8 PS  (volts)', \
            22:'1V5 PS  (volts)', \
            16:'1V  PS  (volts)', \
            0: '1v5aux  (volts)', \
            3: 'Virtex5 temp (deg C)', \
            9: 'PPC  temp (deg C)', \
            31:'Actl temp (deg C)'}

channel_scale={0: 1600.0, \
            7: 250.0, \
            10: 500.0, \
            13: 1000.0, \
            16: 1600.0, \
            22: 1600.0, \
            25: 1600.0, \
            28: 1600.0, \
            3:  4.0, \
            9:  4.0, \
            31: 4.0, \
            11: 65.5, \
            17: 16.375, \
            23: 65.5, \
            26: 32.75, \
            29: 163.75, \
            11: 65.5, \
            14: 163.75}
#the fusion measures temperature in Kelvin, with a positive 5 degree offset.
channel_offset={0: 0,
        7:0, \
        17:0, \
        23:0, \
        26:0, \
        29:0, \
        14:0, \
        11:0, \
        10:0, \
        13:0, \
        16:0, \
        22:0, \
        25:0, \
        28:0, \
        3:-278, \
        9:-278, \
        31:-278}
pwr_state_decode={4: 'Powered off', 3: 'Powered on', 2: 'Sequencing power up',1: 'Sequencing power up',0: 'Sequencing power up'}

shutdown_reason_decode={0:'Cold start or hard reset', 1: 'Crash', 2:'watchdog overflow', 3: 'User shutdown'}


try: 
    if sys.argv[1] == '-h' or sys.argv[1] == '?' or sys.argv[1] == '--help': 
        print '\n Connect to a ROACH Xport, monitor and control the Actel Fusion. \nUsage: ./roach_monitor.py XPORT_IP_ADDRESS [--amps]\n\n Adding [--amps] on the command line will decode current monitoring channels, which are notoriously inaccurate.\n\nJason Manley 2009' 
        exit=True
    else: xport_ip=sys.argv[1]
except: 
    print 'No Xport address specified, defaulting to 192.168.4.20.'

monitor_currents=False
try:
    if sys.argv[2] == '--amps': 
        print 'Decoding currents too.' 
        monitor_currents=True
except: ''
   
if exit:  sys.exit(1)

if monitor_currents:
    channels.update({17:'1V  PS   (amps)', \
            23:'1v5 PS   (amps)', \
            26:'1v8 PS   (amps)', \
            29:'2v5 PS   (amps)', \
            14:'3v3 ATX  (amps)', \
            11:'5V  ATX  (amps)' })

valid_channels=channels.keys()


if not exit:
    # CONNECT TO XPORT
    #=================
    xport=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    xport.connect((xport_ip,10001))
    print 'Connecting to 192.168.4.20 on port 10001...',

    # FLUSH RECEIVE BUFFER
    #======================
    xport.setblocking(False)
    try: raw=xport.recv(10)
    except: print ''
    xport.setblocking(True)

    # CHECK THAT WE"RE TALKING TO FUSION
    # ==================================
    ping=struct.pack('<1B',0x08)
    xport.send(ping)
    raw=xport.recv(10)
    if len(raw) == 1:
        raw_unpacked=struct.unpack('<%iB'%len(raw),raw)[0]
        if raw_unpacked != 0x08: 
            print 'Ping error. Received %i bytes:'%len(raw),raw_unpacked
            xport.close()
            sys.exit()

    # PRINT HEADER
    # =============
    print '\nSerial number: %c%c%c%c%c%c.'%(chr(read(0xB8)),chr(read(0xB9)),chr(read(0xBA)),chr(read(0xBB)),chr(read(0xBC)),chr(read(0xBD)))
    print 'ID: %i, revision %i.%i.%i'%(read(0),read(1),read(2),read(3))
    print 'Board time: %i seconds'%((read(0x06)<<32)+(read(0x07)<<16)+(read(0x08)))

    pwr_state_raw=read(0x280)
    pwr_state=pwr_state_raw&7
    shutdown_reason=(pwr_state_raw&0x300)>>8
    print '\nPower state: %i (%s)'%(pwr_state,pwr_state_decode[pwr_state])
    print 'Reason for last shutdown: %i (%s)'%(shutdown_reason,shutdown_reason_decode[shutdown_reason])


while not exit:
    print '====================================='
    print '        ROACH MONITOR CONTROL    '
    print '====================================='
    print ''
    print '  1) Retrieve details'
    print '  2) Reset crashlog counter '
    print '  3) Power-up ROACH '
    print '  4) Reset ROACH, but not Actel '
    print '  5) Toggle safety-shutdown defeat'
    print '  6) Power down ROACH '
    print '  7) Toggle PPC EEPROM boot (config H)'
    print '  8) Toggle auto power-on after hard-reset.'
    print '  other) Exit'

    selection=raw_input('=>')
    
    if selection == '1': print_details()
    elif selection == '2': clear_crashlog()
    elif selection == '3': power_up()
    elif selection == '4': warm_rst()
    elif selection == '5': toggle_hard_threshold()
    elif selection == '6': power_down()
    elif selection == '7': toggle_config_h()
    elif selection == '8': toggle_power_on_reset()
    else: exit=True

xport.close()
