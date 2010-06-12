import subprocess

def run_in_shell(command_str, verbose=False):
    if verbose:
        print "\r\nRunning \r\n%s" %command_str
    p = subprocess.Popen(command_str, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)
    output = p.stdout.read()
    return(output)

def run_in_sqlite(db_name, sql, verbose=False):
    command = 'sqlite3 %s "%s"' %(db_name, sql)
    output = run_in_shell(command, verbose)
    return(output)
