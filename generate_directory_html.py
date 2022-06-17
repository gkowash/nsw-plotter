N_RUNS = 3

SECTORS = [f'A0{i}' for i in range(1,10)] + [f'A{i}' for i in range(10,17)] + \
          [f'C0{i}' for i in range(1,10)] + [f'C{i}' for i in range(10,17)]
RUNS = list(range(1, N_RUNS+1))
LAYERS = list(range(8))

html_str = ''

for sector in SECTORS:
    html_str = html_str + f'    <li><span class="caret">{sector}</span>\n      <ul class="nested">\n'
    for run in RUNS:
        html_str = html_str + f'        <li><span class="caret">Run {run}</span>\n          <ul class="nested">\n'
        for layer in LAYERS:
            html_str = html_str + f'            <li><a href="#">A01-run{run}-L{layer}</a></li>\n'
        html_str = html_str + '          </ul>\n        </li>\n'
    html_str = html_str + '      </ul>\n    </li>\n\n'

file = open('test.txt', 'w')
file.write(html_str)
file.close()
