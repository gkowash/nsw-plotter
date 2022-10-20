"""
Description:
- Generates plots and plot pages for some or all files using root2html_stgc.py
    - Options
        -a: creates pages for all root files, replacing any already existing ones
        -n: create pages only for new root files, i.e. without an existing page
        -f: creates/updates web pages for only the files specified (with paths) after the -f flag (currently only supports one file per execution)
        -t: specifies plot type (baseline, threshold, pdo, tdo, all); defaults to baseline
        -j: specifies highslide path for root2html_stgc.py (include up to /highslide-5.0.0/highslide)
- Updates html for the file tree that gets loaded into index.html and any other navigation pages
"""

import sys
import os
import getopt

mode = 'new'  # Default mode (new, all, files)
plot_type = 'all'  # Default plot type (baseline, threshold, pdo, tdo, all)
highslide_path = '/highslide'  # Default location on EOS server; set to "/highslide-5.0.0/highslide" for OpenShift server or "None" for .root file directory

# Key phrase unique to file names used for each plot type. (Copy to make_filetree.py if modified)
# NOTE: current key phrases apart from pdo are preliminary; update when appropriate key phrases for others are determined
file_key = {
    'baseline': 'summary_plots.root',
    'threshold': 'outputcanvas.root',
    'pdo': 'pdo_plots.root',
    'tdo': 'summary_plots.root'
}

def main(argv):
    global plot_type
    global mode

    short_options = 'anf:t:j:'
    try:
        opts, args = getopt.gnu_getopt(argv, short_options)
    except getopt.GetoptError:
        print('Argument not recognized; choose from -a, -n, -f, -t, and/or -j. See code for details.\n')
        raise SystemExit

    else:
        for opt, val in opts:
            if opt == '-j':
                global highslide_path
                highslide_path = val
                print('Setting highslide path to ', val)
            if opt == '-a':
                mode = 'all'
            elif opt == '-n':
                mode = 'new'
            elif opt == '-f':
                mode = 'files'
                files = val
                if type(files) == str:
                    files = [files]  # update_files() requires a list of files
            elif opt == '-t':
                plot_type = val
                if plot_type not in ('baseline', 'threshold', 'pdo', 'tdo', 'all'):
                    print('Plot type not recognized by update_plots.py; choose one of: baseline, threshold, pdo, tdo, all')
                    raise SystemExit

    # Update a single file (may support multiple files in the future)
    # 'files' mode is independent of plot type parameter
    if mode == 'files':
        update_files(files)

    # Update plots and pages for a single plot type
    elif plot_type != 'all':
        # Update old and new files
        if mode == 'all':
            update_all(plot_type)
        # Update only new files
        elif mode == 'new':
            update_new(plot_type)

    # Update plots and pages for all plot types
    elif plot_type == 'all':
        # Update old and new files
        if mode == 'all':
            for i, pt in enumerate(file_key.keys()):
                if i ==0:
                    update_all(pt)
                else:
                    update_all(pt, override=True) # Skip user warning so program can execute without interruption
        # Update only new files
        elif mode == 'new':
            for i, pt in enumerate(file_key.keys()):
                update_new(pt)

    # Update file tree for navigation pages (baseline.html, threshold.html, pdo.html, tdo.html)
    print('\n\n\nUpdating html file tree...')
    if plot_type == 'all' or mode == 'files':
        for pt in file_key.keys():
            update_filetree(pt)
    else:
        update_filetree(plot_type)
    print('Update complete.\n')


def update_all(plot_type, override=False):
    # update_all() includes extra safety check to avoid overwriting files
    # Can be skipped using override=True
    if not override:
        confirm = input('\nWarning: root2html_stgc.py will be executed for every available .root file of the specified plot type and will overwrite previously-generated plots and HTML pages. Continue? (y/n)')
        if confirm.lower() != 'y' and confirm.lower() != 'yes':
            print('Exiting program.')
            raise SystemExit

    rootfiles = []
    for root, dirs, files in os.walk('../calibrations/stg'):
        for file in files:
            if file_key[plot_type] in file:
                rootfiles.append(root + '/' + file)

    print('\nExecuting root2html_stgc.py for the following files:\n')
    for file in rootfiles:
        #print('\t' + file.split("/")[-1])
        #test:
        print('\t' + file)
    confirm = input('\nPress "Enter" to confirm.')
    if confirm != '':
        print('Exiting program.')
        raise SystemExit
    else:
        for file in rootfiles:
            filename = file.split("/")[-1]
            print(f'\n\n##### {filename} #####\n')
            update_file(file)

    print('\n\n\n\nPlot updates complete.')


def update_new(plot_type):
    rootfiles = []
    for root, dirs, files in os.walk('../calibrations/stg'):
        for file in files:
            if file_key[plot_type] in file:  # Modify for threshold/pdo/tdo
                if file[:-5] not in dirs:  # Checks whether a directory has previously been generated by root2html_stgc.py
                    rootfiles.append(root + '/' + file)

    print('\nExecuting root2html_stgc.py for the following files:\n')
    for file in rootfiles:
        print('\t' + file.split("/")[-1])

    confirm = input('\nPress "Enter" to confirm.')
    if confirm != '':
        print('Exiting program.')
        raise SystemExit
    else:
        for file in rootfiles:
            print(f'\n\n##### {file.split("/")[-1]} #####\n')
            update_file(file)


def update_file(file):
    # Currently does not support root2html_stgc.py options other than -j (highslide path)
    if highslide_path == None:
        os.system(f'python3 root2html_stgc.py {file} -t {plot_type}')
    else:
        os.system(f'python3 root2html_stgc.py {file} -j {highslide_path} -t {plot_type}')


def update_files(files):
    # multiple files are currently not supported; must enter one at a time.
    # Argument parsing needs to be modified, as getopt does not allow more than one arugment per flag.
    print('\nExecuting root2html_stgc.py for the following files:\n')
    for file in files:
        print('\t' + file.split("/")[-1])

    confirm = input('\nPress "Enter" to confirm.')
    if confirm != '':
        print('Exiting program.')
        raise SystemExit
    else:
        for file in files:
            print(f'\n\n##### {file} #####\n')
            update_file(file)

def update_filetree(plot_type):
    os.system(f'python3 make_filetree.py -t {plot_type}')


if __name__ == '__main__':
    main(sys.argv[1:])
