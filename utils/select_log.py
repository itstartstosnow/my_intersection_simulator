
fname = 'log/190507.log'
fr = open(fname, mode='r')
fw = open(fname.split('.')[0] + '_select.log', 'w')

while 1:
    line = fr.readline()
    if not line:
        break
    if line.find('veh 0,') >= 0:
        fw.write(line)