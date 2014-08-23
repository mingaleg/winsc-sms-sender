#
# WinSC SMS-sender
# Mingalev Oleg aka shhdup
# oleg@mingalev.net
# (c)2013+
#

__author__ = "Mingalev Oleg aka shhdup"


ENCODE = 'cp1251'
SLEEP_TIME = 5           # In seconds
PAGERNAME = 'pager.dat'
MODEM = 'COM7'
DEAD_TIME = 40*60        # In seconds
DEAD_CNT = 3
TRACEBACK_FILE = "grubber.traceback.txt"
RAISE_ALERT_WINDOW = True
LOCKS_FILE = "grubber.locks.bin"
MSG_LOG_FILE = "grubber.msgs.bin"
MSG_LOG_SIZE = 1000
UNLOCK_REQUESTS_FILE = 'grubber.unlock.txt'
SMS_REQUESTS_FILE = 'grubber.sms.txt'
STATISTICS_FILE = 'grubber.statistic.bin'

DEBUG_WITHOUT_SMS = True


from filestructs import FileDict, FileLimitedList

LAST_TIMES = FileDict(LOCKS_FILE)
STAT = FileDict(STATISTICS_FILE)
MSG_LOG = FileLimitedList(MSG_LOG_SIZE, MSG_LOG_FILE)

import os
from time import sleep
if not DEBUG_WITHOUT_SMS:
    from gsmmodem.modem import GsmModem
from datetime import datetime
from io import StringIO

def inc_stat():
    period = datetime.now().strftime('%B %Y')
    today = datetime.now().day
    if period not in STAT:
        STAT[period] = []
    while len(STAT[period]) < today:
        STAT[period] = STAT[period] + [0]
    STAT[period] = STAT[period][:-1] + [STAT[period][-1]+1]


_print = print
def print(*args, **vargs):
    _print(*args, **vargs)
    sio = StringIO()
    _print(*args, file=sio, **vargs)
    MSG_LOG[-1] = MSG_LOG[-1] + sio.getvalue()
    del sio

def grubber(filename, remove_file = True):
    def bytes_from_file(filename, chunksize=8192):
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(chunksize)
                if chunk:
                    for b in chunk:
                        yield b
                else:
                    break

    if not os.path.exists(filename):
        pass
    else:
        bin = bytes(bytes_from_file(filename))
        if remove_file:
            os.remove(filename)
        bin = bin[1:]
        while bin and bin[0] == 0:
            bin = bin[1:]
        while bin:
            bin = bin[1:]
            telephone = bin[:11].decode(ENCODE)
            bin = bin[11:]
            bin = bin[1:]
            msg1 = bytes()
            while bin[0] != 9:
                msg1 += bytes([bin[0]])
                bin = bin[1:]
            msg = bytes()
            bin = bin[1:]
            while bin and bin[0] != 0:
                msg += bytes([bin[0]])
                bin = bin[1:]
            msg = msg + bytes(' ', 'cp1251') + msg1
            msg = msg.decode(ENCODE)
            while bin and bin[0] == 0:
                bin = bin[1:]
            yield {'telephone': telephone, 'msg': msg}


def proceed_message(msg, assured=False):
    truemsg = msg['msg']
    print('=== {telephone} ===\n{msg}'.format(telephone=msg['telephone'], msg=truemsg))

    if not assured:
        foo = msg['telephone'] + msg['msg'][18:]
        if foo not in LAST_TIMES:
            LAST_TIMES[foo] = [datetime.now()]
        else:
            if len(LAST_TIMES[foo]) < DEAD_CNT:
                LAST_TIMES[foo] += [datetime.now()]
            else:
                if (datetime.now() - LAST_TIMES[foo][0]).seconds > DEAD_TIME:
                    LAST_TIMES[foo] += [datetime.now()]
                    LAST_TIMES[foo] = LAST_TIMES[foo][1:]
                else:
                    print('=== TO MANY MESSAGES ===')
                    print('=== IGNORING ===')
                    print()
                    return
    if not DEBUG_WITHOUT_SMS:
        modem.sendSms(msg['telephone'], msg['msg'])
    print('=== OK ===')
    print()
    inc_stat()

def get_balance():
    try:
        response = modem.sendUssd('*100#')
        msg = bytearray.fromhex(response.message).decode('utf_16_be')
        msg = msg.split(' ')[0]
        _print('=> BALANCE: ', msg)
        _print()
    except:
        pass

def proceed_unlock():
    if os.path.exists(UNLOCK_REQUESTS_FILE):
        for tel in open(UNLOCK_REQUESTS_FILE):
            tel = tel.strip()
            if tel in LAST_TIMES:
                del LAST_TIMES[tel]
                _print('! UNLOCKED TEL: ' + tel)
                _print()
        os.remove(UNLOCK_REQUESTS_FILE)

def proceed_sms():
    if os.path.exists(SMS_REQUESTS_FILE):
        with open(SMS_REQUESTS_FILE) as fh:
            foo = fh.readlines()
        os.remove(SMS_REQUESTS_FILE)
        foo = list(map(str.strip, foo))
        foo = list(filter(None, foo))
        while foo:
            tel = foo.pop(0)
            msg = []
            while foo[0] != '==END==':
                msg.append(foo.pop(0))
            foo.pop(0)
            msg = ' '.join(msg)
            MSG_LOG.append('')
            print('== HAND-MADE SMS ==')
            try:
                proceed_message({'telephone': tel, 'msg': msg}, assured=True)
            except Exception as E:
                #print(E)
                import traceback
                with open(TRACEBACK_FILE, 'a') as fh:
                    _print('== ', datetime.now(), ' proceed_sms exception: ', E, file=fh)
                    traceback.print_exc(file = fh)    
                print('== FAIL ==')
                print()

def working_loop(filename):
    while True:
        proceed_unlock()
        proceed_sms()
        sended = False
        for msg in grubber(filename):
            try:
                MSG_LOG.append('')
                sended = True
                proceed_message(msg)
            except Exception as E:
                #print(E)
                import traceback
                with open(TRACEBACK_FILE, 'a') as fh:
                    _print('== ', datetime.now(), ' working_loop exception: ', E, file=fh)
                    traceback.print_exc(file = fh)                
                print('=== FAIL ===')
                print('=== RESENDING! ===')
                print()
                try:
                    proceed_message(msg)
                except:
                    print('=== INSTANT FAIL ===')
                    print('=== IGNORING SMS ===')
                    print()
        if sended:
            get_balance()
        sleep(SLEEP_TIME)

if __name__ == '__main__':
    if not DEBUG_WITHOUT_SMS:
        modem = GsmModem(MODEM)
        modem.connect()
    _print('''# WinSC SMS-sender
# Mingalev Oleg aka shhdup
# oleg@mingalev.net
# (c)2013+''')
    for msg in MSG_LOG:
        _print(msg)
    try:
        get_balance()
        working_loop(PAGERNAME)
    except KeyboardInterrupt as E:
        try:
            modem.close()
        except:
            pass
        _print('Bye!')
    except Exception as E:
        try:
            modem.close()
        except:
            pass
        import traceback
        traceback.print_exc(file = open(TRACEBACK_FILE, 'a'))
        if RAISE_ALERT_WINDOW:
            import ctypes
            ctypes.windll.user32.MessageBoxA(0, "Error!", "GRUBBER.PY", 0)
