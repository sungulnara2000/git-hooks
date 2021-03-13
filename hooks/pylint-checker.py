import os
import re
import sys
from git import Repo
from subprocess import Popen, PIPE

PYLINT_PASS_THRESHOLD = 9


def system(*args, **kwargs):
    """
    Run system command.
    """
    kwargs.setdefault('stdout', PIPE)
    proc = Popen(args, **kwargs)
    out, err = proc.communicate()
    return out


def get_changed_files():
    """
    Get python files from 'files to commit' git cache list.
    """
    files = []
    filelist = system('git', 'diff', '--cached', '--name-status').strip()
    if len(filelist) == 0:
        return files
    for line in filelist.split(b'\n'):
        action, filename = line.strip().split()
        filename = filename.decode("utf-8")
        if filename.endswith('.py') and action != b'D':
            files.append(filename)
    return files

def main():
    changed_py_files = get_changed_files()
        
    results = {}
    for pyfile in changed_py_files:
        pylint = Popen(("pylint -f text %s" % pyfile).split(),
                       stdout=PIPE)
        pylint.wait()

        output = pylint.stdout.read().decode("utf-8")
        results_re = re.compile(r"Your code has been rated at [-+]?\d*\.\d+|\d+/10")
        results[pyfile] = float(results_re.findall(output)[0].split()[-1])


    print("results\n")

    if len(results.values()) > 0:
        print("===============================================")
        print("Final Results:")
        for pyfile in results:
            result = results[pyfile]
            grade = "FAIL" if result < PYLINT_PASS_THRESHOLD else "pass"
            print("[ %s ] %s: %.2f/10" % (grade, pyfile, result))

    if any([(result < PYLINT_PASS_THRESHOLD)
            for result in results.values()]):
        print("Pylint tests failed")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
