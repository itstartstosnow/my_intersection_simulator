import subprocess

simu_result_file = 'log\simu_result' + time.strftime("%Y-%m-%d %H-%M-%S")

for total_flow in [720, 1440, 2880, 4320, 5760]:
    out_bytes = subprocess.check_output(['python', 'main.py', str(total_flow)])
    