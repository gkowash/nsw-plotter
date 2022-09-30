# Script for automatically creating directory tree for stgc plotting application
# Creates html file listing directories, which is then inserted into index.html via JQuery
# Must be positioned in monitor_server folder (or adjust paths accordingly)
# Probably better to avoid JQuery and do with PHP instead, if possible

import os

paths = []

for root, dirs, files in os.walk('../calibrations/stg'):
    for name in dirs:
        #paths.append(os.path.join(root, name))  #Why did I include the root if I just remove it later?
        paths.append(root + '/' + name)
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
        for root, dirs, files in os.walk('../calibrations/stg/'+sector+'/THRCalib/'+run):
            for name in files:
                # Currently only using summary_plots.root
                # outputcanvas.root and [...]_pdo_plots.root are also present
                if 'summary_plots.root' in name:
                    rootfile = name
                    print('Root file: ', rootfile)
                    break
        if rootfile != None:
            name = rootfile[:-5] # Chop off .root extension
            href = f'"/stg/{sector}/THRCalib/{run}/{name}/{name}.html"'
            html += '\t'*5 + f'<li><a href="{href}" class="file" data-file="/stg/{sector}/THRCalib/{run}/{rootfile}">{run}</a></li>\n'
        else:
            html += '\t'*5 + f'<li><a href="#">{run} [nd]</a></li>\n'
    html += '\t'*4 + '</ul>\n'
    html += '\t'*3 + '</li>\n'

html += '\t\t</ul>\n'
html += '\t\t<script src="JavaScript/dropdown.js"></script>'
# ^dropdown.js needs to be executed afer JQuery finishes loads for the menu to function properly
# Solution: stop using JQuery


print('\n\n\n')
print(html)

file = open('filetree.html', 'w')
file.writelines(html)
file.close()
