import glob
import random as rn

# User settings
N_RUNS = 3

# Constants
SECTORS = [f'A0{i}' for i in range(1,10)] + [f'A{i}' for i in range(10,17)] + \
          [f'C0{i}' for i in range(1,10)] + [f'C{i}' for i in range(10,17)]
RUNS = list(range(1, N_RUNS+1))
LAYERS = list(range(8))

# Temporarily assigning random files to links for testing purposes
FILES = glob.glob('data/*.root')

# Construct HTML string
html_str = '  <div id="file-tree-div">\n    <ul id="file-tree">\n'

for sector in SECTORS:
    html_str = html_str + f'      <li><span class="caret">{sector}</span>\n        <ul class="nested">\n'
    for run in RUNS:
        html_str = html_str + f'          <li><span class="caret">Run {run}</span>\n            <ul class="nested">\n'
        for layer in LAYERS:
            # Link to file:
            html_str = html_str + f'              <li><a href="#" class="file" data-file="{rn.choice(FILES)}">{sector}-run{run}-L{layer}</a></li>\n'
        html_str = html_str + '            </ul>\n          </li>\n'
    html_str = html_str + '        </ul>\n      </li>\n'
    if sector == SECTORS[-1]:
        html_str += '    </ul>\n  </div>\n'
    html_str += '\n'

# Save to HTML file
file = open('test.txt', 'w')
file.write(html_str)
file.close()
