#
# WinSC SMS-Sender::Manage-locks
# Mingalev Oleg aka shhdup
# oleg@mingalev.net
# (c)2013+
#

__author__ = "Mingalev Oleg aka shhdup"

from grubber import ENCODE, DEAD_TIME, DEAD_CNT, LOCKS_FILE, UNLOCK_REQUESTS_FILE
from filestructs import FileDict

LAST_TIMES = FileDict(LOCKS_FILE)

from datetime import datetime, timedelta

print('''#
# WinSC SMS-Sender::Manage-locks
# Mingalev Oleg aka shhdup
# oleg@mingalev.net
# (c)2013+
#''')

print('== LOCKED PHONES ==')
LOCKS = []

for tel in LAST_TIMES:
    if len(LAST_TIMES[tel]) >= DEAD_CNT:
        if (datetime.now() - LAST_TIMES[tel][0]).seconds <= DEAD_TIME:
            unlock_time = LAST_TIMES[tel][0] + timedelta(seconds=DEAD_TIME)
            LOCKS.append(tel)
            print('#%02d %s: locked until %s with message:' % (len(LOCKS), tel[:11], unlock_time))
            print(tel[11:])

print('== END ==')

while True:
    print('Unlock telephone #?', end=' ')
    n = input()
    if not n:
        print('Bye!')
        exit()
    else:
        try:
            n = int(n)
            n = LOCKS[n-1]
        except:
            print('Invalid number: ' + str(n))
        try:
            with open(UNLOCK_REQUESTS_FILE, 'a') as fh:
                print(n, file=fh)
            print('== SUCCESS ==')
        except:
            pass
