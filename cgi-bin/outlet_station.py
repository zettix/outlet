#!/usr/bin/python

# (C) 2016 Sean Brennan

""" CGI crap.
"""
import re
import sys
import os
import re
import cgi
import time
import subprocess

# Outlet: 6 : OFF
relay_stat_re = re.compile(r'Outlet: (\d+) : (\S+)')

form = cgi.FieldStorage() # instantiate only once!
outlet_str = form.getfirst('OutPow', '')
what_str = form.getfirst('What', '')

MAJOR_HTML = """
<big><big><big><big><a href=http://www.zettix.com>Zettix.com</a><br>
</big></big></big></big>
<hr style="width: 100%; height: 2px;"><big><big><big><a href="/cgi-bin/outlet_station.py">POWER</a><br>
</big></big></big>
<p>
<form method="POST" action="/cgi-bin/outlet_station.py">
<br>
<table>
<tr><td >
<table>
<tr>
<th>ON</th><th>OFF</th></tr>
<tr><td>
<input type="checkbox" name="OutPow" value="1O" /> 1
</td><td>
<input type="checkbox" name="OutPow" value="1F" /> 1
</td></tr><tr><td>
<input type="checkbox" name="OutPow" value="2O" /> 2
</td><td>
<input type="checkbox" name="OutPow" value="2F" /> 2
</td></tr><tr><td>
<input type="checkbox" name="OutPow" value="3O" /> 3
</td><td>
<input type="checkbox" name="OutPow" value="3F" /> 3
</td></tr><tr><td>
<input type="checkbox" name="OutPow" value="4O" /> 4
</td><td>
<input type="checkbox" name="OutPow" value="4F" /> 4
</td></tr><tr><td>
<input type="checkbox" name="OutPow" value="5O" /> 5
</td><td>
<input type="checkbox" name="OutPow" value="5F" /> 5
</td></tr><tr><td>
<input type="checkbox" name="OutPow" value="6O" /> 6
</td><td>
<input type="checkbox" name="OutPow" value="6F" /> 6
</td></tr><tr><td>
<input type="checkbox" name="OutPow" value="7O" /> 7
</td><td>
<input type="checkbox" name="OutPow" value="7F" /> 7
</td></tr><tr><td>
<input type="checkbox" name="OutPow" value="8O" /> 8
</td><td>
<input type="checkbox" name="OutPow" value="8F" /> 8
</td>
</tr>
</table>
<input type="submit" value="Submit">
</form>
</td><td>
"""

class Bummer(Exception):
  pass

def Log(msg):
  f = open('/var/tmp/Plogfile', 'a')
  f.write(msg)
  f.flush()
  f.close()


class PowerStation:
  def __init__(self):
    self.error  = ''
    self.digits = '12345678'
    self.cmdx = '/home/pi/relay/%s %s > /tmp/relaylog'
    self.res = ''
    self.outlet_status = []
    self.outlet_name_map = {}
    self.outlet_status_map = {}
    self.table_rows = []


  def _GenTableList(self):
    keys = self.outlet_status_map.keys()
    keys.sort()
    for k in keys:
      o_name = k
      o_label = self.outlet_name_map[k]
      status = self.outlet_status_map[k]
      #pre_action = self.cmdx % ('relay_on.sh', o_name)
      o_action = ('<a href="/cgi-bin/outlet_station.py'
                  '?OutPow=%s%s">TURN ON</a>' % (o_name, 'O'))
      o_status = ('<td class=off_state><a href="/cgi-bin/outlet_station.py'
                  '?OutPow=%s%s">OFF</a></td>' % (o_name, 'O'))
      if status == 'ON':
        #pre_action = self.cmdx % ('relay_on.sh', o_name)
        o_action = ('<a href="/cgi-bin/outlet_station.py'
                    '?OutPow=%s%s">TURN OFF</a>' % (o_name, 'F'))
        o_status = ('<td class=on_state><a href="/cgi-bin/outlet_station.py'
                    '?OutPow=%s%s">ON</a></td>' % (o_name, 'F'))
      
      td = '<tr><td class=outlet>%s</td><td class=labbie>%s</td>%s<td>%s</td></tr>' % (
        o_name, o_label, o_status, o_action)
      Log('Appended td: %s\n' % td)
      self.table_rows.append(td)

  def _GetOutletName(self, line):
    lineparts = line.split(' ')
    dirty_outlet = lineparts[0]
    label = ' '.join(lineparts[1:])
    string_outlet = dirty_outlet.split(':')[0]
    int_outlet = int(string_outlet)
    return (int_outlet, label)


  def GetStats(self):
    out = []
    p2 = subprocess.Popen(["cat", "/home/pi/relay/CONFIG"], stdout=subprocess.PIPE)
    output = p2.communicate()[0]
    for inl in output.split('\n'):
      Log("INL:[%s]" % inl)
      if len(inl) == 0:
        continue
      k, v = self._GetOutletName(inl)
      self.outlet_name_map[k] = v
    out.append("<pre>%s</pre>" % output)
    p2 = subprocess.Popen(["/home/pi/relay/parse_gpio_out.py", "www-data"],
                          stdout=subprocess.PIPE)
    output2 = p2.communicate()[0]
    for inl in output2.split('\n'):
      Log("OLT:[%s]" % inl)
      if len(inl) == 0:
        continue
      gob = relay_stat_re.search(inl)
      if (gob):
         outie = int(gob.group(1))
         stat = gob.group(2)
         self.outlet_status_map[outie] = stat
         Log("gob: %d=%s\n" % (outie, stat))
      else:
        Log("NOTAGUN: %s\n" % inl)
    Log("\nself.outlet_name_map:%s\nself.outlet_status_map:%s\n" % (
        self.outlet_name_map.keys(), self.outlet_status_map.keys()))
    for keykey in self.outlet_name_map.keys():
      iggy = "%s  %s  %s" % (keykey, self.outlet_name_map[keykey],
                                      self.outlet_status_map[keykey])
      out.append(iggy)
      
    out.append("<pre>%s</pre>" % output2)
    return '\n'.join(out)


  def ProcessCommand(self):
    #global flip_str
    global outlet_str
    #global form
    global what_str
    
    flip_str = 'X'
    outlet_s = 'Z'
    # outlet_str = form.getfirst('OutPow', '')
    outlet_list = form.getlist('OutPow')
    what_str = form.getfirst('What', '')
    self.res += " Form--%s-- <br>" % form
    self.res += " what--%s-- <br>" % what_str
    self.res += " outwws--%s-- <br>" % outlet_str
    self.res += " Outlet:--%s----%s-- <br>" % (outlet_str, outlet_str)
    for outlet_str in outlet_list:
      outlet_str_0 = outlet_str
      if len(outlet_str_0) == 2:
        flip_str = outlet_str_0[1]
        outlet_s = outlet_str_0[0]
      if flip_str in ['O', 'F'] and outlet_s in self.digits:
        outnum = self.digits.index(outlet_s)
        if flip_str == 'O':
          cmd = self.cmdx % ('relay_on.sh', outnum + 1)
          self.res += 'Turning Outlet %d to ON!' % (outnum + 1)
        else:
          cmd = self.cmdx % ('relay_off.sh', outnum + 1)
          self.res += 'Turning Outlet %d to OFF!' % (outnum + 1)
        r = os.system(cmd)
        if r < 0:
          Log("Error with cmd: %s" % cmd)

    
  def EmitHtml(self):
    # The thing I like about this is, the commands have run.
    # So the status is current.
    self.outlet_status = []
    self.outlet_name_map = {}
    self.outlet_status_map = {}
    statstring = self.GetStats()
    
    print "Content-Type: text/html"
    print
    print """\
<html>
<title>Outlet Station</title>
<style>
a:link {
   color: #99ff99;
}

a:active {
   color: #33cc00;
}

a:visited {
   color: #33cc00;
}

.on_state {
  color: black;
  background-color: yellow;
  width: 50px;
  padding: 10px;
  margin: 10px;
  border: 5px solid gray;
  border-radius: 10px;
}

.off_state {
  color: white;
  background-color: black;
  width: 50px;
  padding: 10px;
  margin: 10px;
  border: 5px solid gray;
  border-radius: 10px;
}

body {
  color: rgb(192, 192, 192);
  background-color: rgb(0, 0, 0);
}

table {
  border: 5px solid gray;
  border-radius: 30px;
  padding: 15px;
  margin: 5px;
  background-color: #202060;
}

.outlet {
  font-size: 160%;
  color: #ff2288;
  background-color: #444444;
}

td {
  border: 7px solid gray;
  border-radius: 7px;
  text-align: center;
  border: 5px solid #888888;
  border-radius: 30px;
  background-color: #000080;
  margin: 30px;
  padding: 15px;
}

.labbie {
  font-size: 130%;
  font-style: italic;
  background-color: #111111;
}

.blacky {
  background-color: pink;
}

</style>
<body>"
"""
    print MAJOR_HTML
    # print "Stuff..."
    # print self.res
    # print statstring
    self._GenTableList()
    print """<table>"""
    print """<th><b>Outlet</b></th>"""
    print """<th><b>Label</b></th>"""
    print """<th><b>Status</b></th>"""
    print """<th><b>Action</b></th>"""
    for td in self.table_rows:
      print td
    print """</table></td></tr>"""
    print """</table>"""
    print """<a href=/power.html>Go Back<a/>"""
    print """</body></html>"""

  def Run(self):
    self.ProcessCommand()
    self.EmitHtml()


if __name__ == '__main__':
  frak = PowerStation()
  flip_str = 'ON'
  outlet_str = '1'
  frak.Run()
  #Log('\n'.join(frak.cmd_log))
