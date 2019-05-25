import sys
sys.path.append("../")

fname = r'C:\ProjectsData\GraduateProject\my-intersection-simulator\log\log 2019-05-25 21-02-04.log'
fr = open(fname, mode='r')
fw = open(fname.split('.')[0] + '_cut.log', 'w')

while 1:
    line = fr.readline()
    if not line:
        break
    if line.split(',')[0] == 't':
        fw.write(line)
    elif int(line.split(',')[0]) <= 6000:
        fw.write(line)
    else:
        break
