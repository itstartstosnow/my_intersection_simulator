import sys
sys.path.append("../")

fname = '../log/log 2019-05-22 20-58-24.log'
fr = open(fname, mode='r')
fw = open(fname.split('.')[0] + '_cut.log', 'w')

while 1:
    line = fr.readline()
    if not line:
        break
    if line.split(',')[0] == 't':
        fw.write(line)
    elif int(line.split(',')[0]) <= 1800:
        fw.write(line)
    else:
        break