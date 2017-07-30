#!/usr/bin/python
import os
import subprocess

example = """ +-----+-----+---------+------+---+-Model B2-+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
 |   2 |   8 |   SDA.1 |   IN | 1 |  3 || 4  |   |      | 5V      |     |     |
 |   3 |   9 |   SCL.1 |   IN | 1 |  5 || 6  |   |      | 0v      |     |     |
 |   4 |   7 | GPIO. 7 |  OUT | H |  7 || 8  | 1 | ALT0 | TxD     | 15  | 14  |
 |     |     |      0v |      |   |  9 || 10 | 1 | ALT0 | RxD     | 16  | 15  |
 |  17 |   0 | GPIO. 0 |  OUT | A | 11 || 12 | B | OUT  | GPIO. 1 | 1   | 18  |
 |  27 |   2 | GPIO. 2 |  OUT | C | 13 || 14 |   |      | 0v      |     |     |
 |  22 |   3 | GPIO. 3 |  OUT | D | 15 || 16 | E | OUT  | GPIO. 4 | 4   | 23  |
 |     |     |    3.3v |      |   | 17 || 18 | F | OUT  | GPIO. 5 | 5   | 24  |
 |  10 |  12 |    MOSI |   IN | 0 | 19 || 20 |   |      | 0v      |     |     |
 |   9 |  13 |    MISO |   IN | 0 | 21 || 22 | G | OUT  | GPIO. 6 | 6   | 25  |
 |  11 |  14 |    SCLK |   IN | 0 | 23 || 24 | 1 | IN   | CE0     | 10  | 8   |
 |     |     |      0v |      |   | 25 || 26 | 1 | IN   | CE1     | 11  | 7   |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 |  28 |  17 | GPIO.17 |   IN | 0 | 51 || 52 | 0 | IN   | GPIO.18 | 18  | 29  |
 |  30 |  19 | GPIO.19 |   IN | 0 | 53 || 54 | 0 | IN   | GPIO.20 | 20  | 31  |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+-Model B2-+---+------+---------+-----+-----+"""
num_outlets = 8

import os
import sys

def GetStats(txt):
  current_state = [x for x in range(num_outlets)]
  for l in txt.split('\n'):
    if 'GPIO. ' in l:
      #here we go.
      all_fields = l.split()
      current_index = 0
      for x in range(len(all_fields)):
        if all_fields[x] == 'GPIO.':
          status = 'N'
          if all_fields[x+3] == 'OUT':
            status = all_fields[x+5]
          elif all_fields[x-2] == 'OUT':
            status = all_fields[x-4]
          if status == '1':
            status = 'OFF'
          else:
            status = 'ON'
          outlet = int(all_fields[x+1])
          # print 'Out: %d stat: %s' % (outlet, status)
          current_state[outlet] = status

  return current_state


def PrettyPrint(l):
  binval = 0;
  for x in range(len(l)):
    print 'Outlet: %d : %s' % (x + 1, l[x])
    if l[x]  == "OFF":
      binval += 2 ** x;
  return binval

if __name__ == '__main__':
  username = 'pi'
  if len(sys.argv) > 1:
    username = sys.argv[1]
  whitelist = {
    'pi': '/home/pi/outlet/relay/oldstat',
    'www-data': '/var/www/data/oldstat'
  }
  # test
  if username not in whitelist.keys():
    print "I don't know you!  Get out %s!:" % username
    sys.exit(1) 
  oldval = whitelist[username]
  prog = "/usr/local/bin/gpio"
  if os.path.exists(prog):
    out = subprocess.check_output([prog, 'readall'])
    binval = PrettyPrint(GetStats(out))
    open(oldval, "w").write("%d" % binval)
  else:
    print "Testing only"
    PrettyPrint(GetStats(example))
