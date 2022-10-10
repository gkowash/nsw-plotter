# Script for automatically creating directory tree for stgc plotting application
# Creates html file listing directories, which is then inserted into index.html via JQuery
# Must be positioned in monitor_server folder (or adjust paths accordingly)
# It would be better to avoid JQuery and do this with PHP instead, but I believe the default NGINX image does not support PHP

import os

paths = []

for root, dirs, files in os.walk('../calibrations/stg'):
    for dir in dirs:
        paths.append(root + '/' + dir)
        print(paths[-1])
        print("")


# Currently paths look like ../calibrations/stg/STG-EA-S[##]/THRCalib/run[########]
#paths_split = list(map(lambda p: p.split('/')[3:], paths))
paths_split = list(map(lambda p: p.split('/'), paths))
sectors = [path[-1] for path in paths_split if len(path)==4]  # len(path)==4 excludes subpaths of the "STG-EA-S[##]" directories

runs_per_sector = {}
for sector in sectors:
    runs_per_sector[sector] = [path[-1] for path in paths_split if sector in path and len(path)==6]  # len(path)==6 selects only the "run[########]" folders


print(runs_per_sector)

html = '\t\t<ul id="file-tree">\n'

for sector in sectors:
    html += '\t'*3 + f'<li><span class="caret">{sector.split("-")[-1]}</span>\n'
    html += '\t'*4 + '<ul class="nested">\n'

    for run in runs_per_sector[sector]:
        rootfile = None
        has_plotpage = False  # Indicates whether root2html_stgc.py has created a plot page for this file yet
        for root, dirs, files in os.walk('../calibrations/stg/'+sector+'/THRCalib/'+run):
            for name in files:
                # Currently only using summary_plots.root
                # outputcanvas.root and [...]_pdo_plots.root are also present
                if 'summary_plots.root' in name:
                    # Consider adding command line option to specify other file names like pdo_plots (see doc for more details)
                    rootfile = name
                    #print('Root file: ', rootfile)
                    if name[:-5] in dirs:  # checks for directory created by root2html_stgc.py
                        has_plotpage = True
                    break
        if rootfile != None:
            name = rootfile[:-5] # Chop off .root extension
            if has_plotpage:
                href = f'/stg/{sector}/THRCalib/{run}/{name}/{name}.html'
            else:
                href = '#'
            html += '\t'*5 + f'<li><a href="{href}" class="file" data-file="/stg/{sector}/THRCalib/{run}/{rootfile}">{run}</a></li>\n'
        else:
            html += '\t'*5 + f'<li><a href="#">{run} [nd]</a></li>\n'
    html += '\t'*4 + '</ul>\n'
    html += '\t'*3 + '</li>\n'

html += """
\t\t</ul>\n
\t\t<script src="JavaScript/dropdown.js"></script>
\t\t<script src="JavaScript/browser_loader.js"></script>
"""
# ^dropdown.js and browser_loader.js need to be executed afer JQuery finishes loading to work properly


print('\n\n\n')
print(html)

file = open('filetree_baseline.html', 'w')  # Modify name for threshold/pdo/tdo
file.writelines(html)
file.close()
