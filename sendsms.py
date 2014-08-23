#
# Simple SMS-sender
# Mingalev Oleg aka shhdup
# oleg@mingalev.net
# (c)2013+
#

__author__ = "Mingalev Oleg aka shhdup"


from grubber import SMS_REQUESTS_FILE

if __name__ == '__main__':
    print('''# Simple SMS-Sender
# Mingalev Oleg aka shhdup
# oleg@mingalev.net
# (c)2013+''')
    print('TEL:', end=' ')
    tel = input()
    if tel.startswith('+7'):
        tel = '8' + tel[2:]
    if len(tel) != 11 or not tel.isnumeric:
        print('== ERROR ==')
        print('Invalid number!')
        print('Press any key to exit...')
        input()
        exit()
    else:
        msg = []
        while True:
            print('MSG:', end=' ')
            cs = input()
            if cs:
                msg.append(cs)
            else:
                if msg:
                    break
                else:
                    print('Enter your message')
        msg.append('==END==')
        print('== TRYING TO ENQUEUE ==')
        with open(SMS_REQUESTS_FILE, 'a') as fh:
            print(tel, file=fh)
            for line in msg:
                print(line, file=fh)
        print('== OK ==')
        print('Press any key to exit...')
        input()
