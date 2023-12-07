import subprocess

def find_files(file_name):
    command = ['locate', file_name]

    output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]
    output = output.decode()

    search_results = output.split('\n')

    return search_results

print(find_files('rocketleague.exe'))