#!/usr/bin/env python
"""
*******
UPDATE DESCRIPTION
    Modified from original in June-September 2022 by Griffin Kowash for sTGC plotter project.
    HTML write functions now optionally organize plots into columns by strip, pad, and wire.
    Some minor cosmetic changes have also been made.

    The code has been updated to work with Python 3.
    Funcitonality has only been verified for certain use cases, so the original
    Python 2 version will be more reliable for general purpose use.

    Original description is below.
*******

NAME
    root2html.py - generates html and images for displaying TCanvases

SYNOPSIS
    root2html.py [OPTIONS] file.root [file2.root ...]

DESCRIPTION
    root2html is a script for generating an html page for displaying plots.
    root2html expects you to pass a root file, filled with TCanvases,
    possibly organized in TDirectories.  The canvases presumably have plots
    that you have pre-made and styled however you like.  root2html inspects
    the root file and walks its directories.  Then, for each canvas, it
    inspects  all objects that have been drawn to the canvas, and gets
    statistics depending on the object's type.  These stats are displayed in
    the caption when you click on a figure.  Then, root2html creates eps and
    gif/png images for each of the plots, and generates an html page
    containing and linking all the information.

    When viewing the output html, note that you can click-up more than one
    figure at a time, and drag them around the screen.  That javascript magic
    is done with the help of this library: http://highslide.com/.

INSTALLATION
    Assuming you have a working ROOT installation with PyROOT, the only other
    requirement is that you download the highslide javascript library at
    http://highslide.com/, unzip it, and set the highslide_path variable to
    point to the path: highslide-<version>/highslide (see below).

OPTIONS
    -h, --help
        Prints this manual and exits.

    -p PATTERN, --pattern=PATTERN
        Regex pattern for filtering the TCanvas paths processed.  The pattern
        is matched against the full paths of the TCanvases in the root file.

    -j PATH, --highslide=PATH
        Overrides the default path to highslide.

    -t PLOT TYPE, --type=PLOT TYPE
        Specifies plot type (baselines, threshold, pdo, tdo) for HTML page. Added for root2html_stgc.py

AUTHORS
    Ryan Reece  <ryan.reece@cern.ch>
    Tae Min Hong  <tmhong@cern.ch>
    Alex Tuna  <tuna@cern.ch>

LICENSE
    Copyright 2011-2015 The authors
    License: GPL <http://www.gnu.org/licenses/gpl.html>

SEE ALSO
    ROOT <http://root.cern.ch>
    Highslide <htindex.html
tp://highslide.com/>

2011-02-16
"""
#------------------------------------------------------------------------------

import os, sys, getopt, io  # added io for Python3-ification of class HighSlideRootFileIndex
import ctypes  # Also adding this for Python3
import time
import re
import math

import ROOT
ROOT.gROOT.SetBatch(True)
#try:
#    import rootlogon # your custom ROOT options, comment-out this if you don't have one
#except:
#    print('Could not import rootlogon')
ROOT.gErrorIgnoreLevel = 1001

path_of_this_file = os.path.abspath( __file__ )
dir_of_this_file = os.path.dirname(os.path.abspath( __file__ ))

#------------------------------------------------------------------------------

## global options
highslide_path = os.path.join(dir_of_this_file, 'highslide-5.0.0/highslide')
plot_type = '[plot type unspecified]'  # specifies plot type (baseline, threshold, pdo, tdo) for HTML page
img_format = 'png' # gif or png
img_height = 450 # pixels
thumb_height = 120 # pixels
quiet = True

#______________________________________________________________________________
def main(argv):
    ## option defaults
    pattern = ''
    global highslide_path
    name_html = True  # assign name to HTML output file using rootfile name (defaults to index.html)

    ## parse options
    _short_options = 'hp:j:t:'
    _long_options = ['help', 'pattern=', 'highslide=', 'type=']
    try:
        opts, args = getopt.gnu_getopt(argv, _short_options, _long_options)
    except getopt.GetoptError:
        print('getopt.GetoptError\n')
        print(__doc__)
        sys.exit(2)
    for opt, val in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            sys.exit()
        if opt in ('-p', '--pattern'):
            pattern = val
        if opt in ('-j', '--highslide'):
            highslide_path = val
        if opt in ('-t', '--type'):
            global plot_type
            plot_type = val

    print('  root2html_stgc.py  ----------------------------------------------------')

    assert len(args) > 0

    t_start = time.time()
    n_plots = 0

    ## make indexes
    for path in args:
        path_wo_ext = strip_root_ext(path)
        if name_html:
            name = os.path.join(path_wo_ext, path_wo_ext.split('/')[-1] + '.html')
        else:
            name = os.path.join(path_wo_ext, 'index.html')
        index = HighSlideRootFileIndex(name)
        index.write_head(os.path.basename(path), full_path=path)  # 'full_path' argument added for root2html_stgc.py
        n_plots += index.write_root_file(path, pattern)
        index.write_foot()
        index.close()
        print('  %s written.' % name)

    t_stop = time.time()
    print('  # plots    = %i' % n_plots)
    print('  time spent = %i s' % round(t_stop-t_start))
    print('  avg rate   = %.2f Hz' % (float(n_plots)/(t_stop-t_start)))
    print('  Done.')

#------------------------------------------------------------------------------
class HighSlideRootFileIndex(io.FileIO): # old version: "file):"
    #__________________________________________________________________________
    def __init__(self, name='index.html'):
        make_dir_if_needed(name)
        super(HighSlideRootFileIndex, self).__init__(name, 'w')
        self.dirname = os.path.dirname(name)
        self.highslide_path = highslide_path # '/home/reece/projects/highslide_dev/highslide-4.1.9/highslide'
        self.previous_level = 0
        self.pwd = None
    #__________________________________________________________________________
    def write_head(self, title, mod=True, full_path=None):
        head_template = r"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title>%(title)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <script type="text/javascript" src="%(highslide_path)s/highslide-full.js"></script>
    <link rel="stylesheet" type="text/css" href="%(highslide_path)s/highslide.css" />
    <link rel="stylesheet" type="text/css" href="/css/style.css">
    <script type="text/javascript">
        //<![CDATA[
        hs.graphicsDir = '%(highslide_path)s/graphics/';
        hs.wrapperClassName = 'wide-border';
        //]]>
    </script>
    <script type="text/javascript">
        //<![CDATA[
        function toggle_more(objID) {
            if (!document.getElementById) return;
            var ob = document.getElementById(objID).style;
            ob.display = (ob.display == 'block')?'none':'block';
            var ob2 = document.getElementById('link:'+objID);
            ob2.className = (ob2.className == 'open') ? 'closed' : 'open';
        }
        //]]>
    </script>
    <style type="text/css">
        <!--
        body
        {
            font-family: sans-serif;
            overflow-x: hidden;
            overflow-y: scroll;
        }
        h1
        {
            display: block;
            border-bottom: 1px black solid;
            padding-bottom: 5px;
            font-size: 1.0em;
        }
        div.dir_header
        {
            font-size: 1.5em;
        }
        div.dir_header a, div.highslide-heading a
        {
            cursor: pointer;
        }
        div.dir_header a.open:before
        {
            font-family: monospace;
            content: "[-] ";
        }
        div.dir_header a.closed:before
        {
            font-family: monospace;
            content: "[+] ";
        }
        div.more
        {
            display: none;
            clear: both;
            margin-left: 40px;
        }
        div.foot
        {
            display: block;
            margin-top: 5px;
            border-top: 1px black solid;
            padding-top: 5px;
            padding-bottom: 15px;
        }
        div.foot div.user, div.foot div.date
        {
            display: inline;
            float: left;
            margin-right: 40px;
        }
        div.foot div.powered_by, div.foot div.valid
        {
            display: inline;
            float: right;
            margin-left: 40px;
        }
        /*
        a:link {color: #06989a;}
        a:visited {color: #bf2dae;}
        a:hover {text-decoration: underline;}
        */
        table td, table th
        {
            padding-top: 0;
            padding-bottom: 0;
            padding-left: 0px;
            padding-right: 20px;
            font-family: monospace;
            font-size: 10px;
            text-align: right;
        }
        /*
        table td+td, table th+th
        {
            text-align: right;
        }
        */
        table th
        {
            font-weight: bold;
        }

    </style>
</head>
<body>
<div id="body">
"""
        if mod:  # adds navigation bar for plots-stgc application to top of page
            # For f-string, note that double curly braces are an escape character and only output a single curly brace {
            head_template += f"""    <div id="nav-placeholder"></div>
    <script src="/JavaScript/jquery-3.6.0.js" type="text/javascript"></script>
    <script>
        $(function(){{
            $("#nav-placeholder").load("/html/nav.html");
        }});
    </script>
    <h2>{plot_type}</h2>
    <h1>{full_path}</h1>
    """
        self.write((head_template % {
                'title' : title,
                'highslide_path' : self.highslide_path }).encode('utf-8')) # Encode added for Python 3
    #__________________________________________________________________________
    def write_foot(self):
        ## close preivous more divs
        while self.pwd:
            self.write(("</div> <!-- %s -->\n" % self.pwd).encode('utf-8'))
            pwd_split = self.pwd.split('/')[:-1]
            if pwd_split:
                self.pwd = os.path.join(*(pwd_split))
            else:
                self.pwd = ''
        foot_template = r"""
</div> <!-- body -->
<div class="foot">
    <div class="user">%(user)s</div>
    <div class="date">%(date)s</div>
    <div class="powered_by">produced with <a href="https://svnweb.cern.ch/trac/penn/browser/reece/rel/root2html/trunk/root2html.py">root2html.py</a></div>
    <div class="valid"><a href="http://validator.w3.org/check?uri=referer">valid xhtml</a></div>
</div>
</body>
</html>
"""
        self.write((foot_template % {
                'user' : os.environ['USER'],
                'date' : time.ctime() }).encode('utf-8'))
    #__________________________________________________________________________
    def write_root_file(self, path, pattern='', mod=True):
        n_plots = 0
        rootfile = ROOT.TFile(path)
        # Following lines are modified from original--organizes canvases into strip, pad, and wire columns for the HTML page
        if mod:
            strip = '<div class="column">\n\t<h2>Strip</h2>'
            pad = '<div class="column">\n\t<h2>Pad</h2>'
            wire = '<div class="column">\n\t<h2>Wire</h2>'

        for dirpath, dirnames, filenames, tdirectory in walk(rootfile):
            for key in filenames:
                obj = tdirectory.Get(key)

                # Hack for when we find TH1, TH2 instead of TCanvas
                new_obj = None
                if issubclass(obj.__class__, ROOT.TH1) or issubclass(obj.__class__, ROOT.TH1):
                    new_obj = ROOT.TCanvas(obj.GetName(), obj.GetTitle(), 500, 500)
                    new_obj.cd()
                    obj.SetLineColor(ROOT.kRed-3)
                    obj.SetMarkerColor(ROOT.kRed-3)
                    obj.Draw('PE')
                    obj = new_obj

                # Put TCanvas on html
                if isinstance(obj, ROOT.TCanvas):
                    root_dir_path = dirpath.split(':/')[1]
                    root_key_path = os.path.join(root_dir_path, key)
                    if pattern and not re.match(pattern, root_key_path):
                        continue
                    print(os.path.join(dirpath, key).split(':')[-1])
                    # Include following lines if dir_header is desired at the top of each column:
                    #if mod:
                    #    dir_header = self.write_dir_header(dirpath, mod=True)
                    #    strip += dir_header
                    #    pad += dir_header
                    #    wire += dir_header
                    #if not mod:
                    #    self.write_dir_header(dirpath)
                    self.write_dir_header(dirpath)  # Remove this line if uncommenting above
                    full_path = os.path.join(self.dirname, root_key_path)
                    if mod:
                        canvas_html = self.write_canvas(obj, full_path, mod=True)
                        if 'strip' in key.lower() or 'sfeb' in key.lower():
                            strip += canvas_html
                        elif 'pad' in key.lower() or 'pfeb' in key.lower():
                            pad += canvas_html
                        elif 'wire' in key.lower():
                            wire += canvas_html
                        else:
                            print('\t>>> Canvas "', key, '" cannot be classified as strip/sFEB, pad/pFEB, or wire')
                    else:
                        self.write_canvas(obj, full_path)

                    n_plots += 1

        if mod:
            strip += '</div>\n'
            pad += '</div>\n'
            wire += '</div>\n'
            self.write(strip.encode('utf-8'))
            self.write(pad.encode('utf-8'))
            self.write(wire.encode('utf-8'))

        rootfile.Close()
        return n_plots
    #__________________________________________________________________________
    def write_dir_header(self, path, mod=True):
        path_split = path.split(':/')
        rootfile = path_split[0]
        dirpath = path_split[1]
        dirpath.rstrip('/')

        if mod:  # Added in case dir header is desired at the top of each column; currently not in use
            header_html = ''

        if self.pwd is None:
            if mod:
                header_html += """\n<h1>%s</h1>\n""" % rootfile
            else:
                self.write(("""\n<h1>%s</h1>\n""" % rootfile).encode('ustriptf-8')) # encode added for Python 3
            self.pwd = ''

        if dirpath != self.pwd:
            ## pop
            rel_path = relpath(dirpath, self.pwd)
            while rel_path.startswith('../'):
                if mod:
                    header_html += "</div> <!-- %s -->\n" % self.pwd
                else:
                    self.write(("</div> <!-- %s -->\n" % self.pwd).encode('utf-8'))
                self.pwd = os.path.join(*(self.pwd.split('/')[:-1])) if self.pwd.count('/') else ''
                rel_path = relpath(dirpath, self.pwd)

            ## push
            rel_path = relpath(dirpath, self.pwd)
            while rel_path.count('/'):
                path_down_one_dir = '%s:/%s' % (rootfile, os.path.join(self.pwd, rel_path.split('/')[0]))
                if mod:
                    header_html += self.write_dir_header(path_down_one_dir, mod=True)
                else:
                    self.write_dir_header(path_down_one_dir, mod=False)
                rel_path = relpath(dirpath, self.pwd)

            id_name = dirpath.replace('/', '_')
            dir_name = dirpath.split('/')[-1]
            self.pwd = dirpath
            if mod: #modified September 2022
                header_html += """\n\t<div class="dir_header"><a id="link:%s" class="closed" onclick="toggle_more('%s')">%s</a></div>\n""" % (id_name, id_name, dir_name)
                header_html += """\t<div id="%s" class="more">\n""" % id_name
            else: #original
                self.write(("""\n<div class="dir_header"><a id="link:%s" class="closed" onclick="toggle_more('%s')">%s</a></div>\n""" % (id_name, id_name, dir_name)).encode('utf-8'))
                self.write(("""<div id="%s" class="more">\n""" % id_name)).encode('utf-8')

        if mod:
            return header_html

    #__________________________________________________________________________
    def write_canvas(self, canvas, basepath, mod=True):
        name = canvas.GetName()
        make_dir_if_needed(basepath)
        ## save eps
        eps = basepath + '.eps'
        canvas.SaveAs(eps)
        ## save img
        if img_format == 'gif':
            img = convert_eps_to_gif(eps)
        elif img_format == 'png':
            img = convert_eps_to_png(eps)
        ## save thumb
        if img_format == 'gif':
            thumb = convert_eps_to_thumb_gif(eps)
        elif img_format == 'png':
            thumb = convert_eps_to_thumb_png(eps)
        ## additional formats
        formats = [] # ['.png', '.pdf', '.C']
        for format in formats:
            canvas.SaveAs(basepath + format)
        ## convert to relpaths
        ## use locally defined relpath because os.path.relpath does not
        ## exist in Python 2.5.
        eps = relpath(eps, self.dirname)
        img = relpath(img, self.dirname)
        thumb = relpath(thumb, self.dirname)
        ## write xhtml
        fig_template = r"""
    <a href="%(img)s" class="highslide" rel="highslide">
      <img src="%(thumb)s" alt="%(name)s" title="%(name)s"/>
    </a>
"""
        heading_template = r"""    <div class="highslide-heading">
      <a title="%(path)s">%(name)s</a>&nbsp;[&nbsp;<a href="%(eps)s">eps</a>&nbsp;|&nbsp;<a href="%(img)s">%(format)s</a>&nbsp;]
    </div>
"""
        caption_template = r"""    <div class="highslide-caption">
      %s    </div>
"""
        fig_html = fig_template % {
                    'name'  : name,
                    'img'   : img,
                    'thumb' : thumb }
        heading_html = heading_template % {
                'path'  : basepath,
                'name'  : name,
                'eps'   : eps,
                'img'   : img,
                'format': img_format}
        if mod:
            canvas_html = fig_html + heading_html
        else:
            self.write(fig_html.encode('utf-8'))
            self.write(heading_html.encode('utf-8'))
        ## get stats
        stats = get_canvas_stats(canvas)
        if stats:
            clean_stats_names(stats)
            tab = convert_stats_to_table(stats)
            html_tab = convert_table_to_html(tab)
            if mod:
                canvas_html += caption_template % html_tab
            else:
                self.write((caption_template % html_tab).encode('utf-8'))
        if mod:
            return canvas_html


#------------------------------------------------------------------------------
# free functions
#------------------------------------------------------------------------------

#__________________________________________________________________________
def get_canvas_stats(canvas):
    prims = [ p for p in canvas.GetListOfPrimitives() ]
    prims.reverse() # to match legend order
    names_stats = []
    for prim in prims:
        if isinstance(prim, ROOT.TFrame):
            continue # ignore these
        elif isinstance(prim, ROOT.TPad):
            names_stats.extend( get_canvas_stats(prim) )
        else:
            names_stats.extend( get_object_stats(prim) )
    return names_stats

#__________________________________________________________________________
def get_object_stats(h):
    names_stats = []
    name = h.GetName()
    stats = {}
    if isinstance(h, ROOT.TH1) and not isinstance(h, ROOT.TH2):
        nbins       = h.GetNbinsX()
        entries     = h.GetEntries()
        err = ctypes.c_double(0)  #ROOT.double(0)
        integral    = h.IntegralAndError(0, nbins+1, err)
#        integral    = h.Integral(0, nbins+1)
#        err         = math.sqrt(float(entries))*integral/entries if entries else 0
        mean        = h.GetMean()
        rms         = h.GetRMS()
        under       = h.GetBinContent(0)
        over        = h.GetBinContent(nbins+1)
        stats['entries'] = '%i'   % round(entries)
        stats['int']     = ('%i' % round(integral)) if integral >= 100 else ('%.3g' % integral)
        stats['err']     = '%.2g' % err.value
        stats['mean']    = '%.3g' % mean
        stats['rms']     = '%.3g' % rms
        stats['under']   = '%.3g' % under
        stats['over']    = '%.3g' % over
        names_stats.append( (name, stats) )
    elif isinstance(h, ROOT.TH2):
        nbins_x     = h.GetNbinsX()
        nbins_y     = h.GetNbinsY()
        entries     = h.GetEntries()
        err = ctypes.c_double(0) #ROOT.Double_t(0)
        integral    = h.IntegralAndError(0, nbins_x+1, 0, nbins_y+1, err)
#        integral    = h.Integral(0, nbins_x+1, 0, nbins_y+1)
#        err         = math.sqrt(float(entries))*integral/entries if entries else 0
        mean_x      = h.GetMean(1)
        rms_x       = h.GetRMS(1)
        mean_y      = h.GetMean(2)
        rms_y       = h.GetRMS(2)
        stats['entries'] = '%i'   % round(entries)
        stats['int']     = ('%i' % round(integral)) if integral >= 100 else ('%.3g' % integral)
        stats['err']     = '%.2g' % err.value
        stats['mean_x']  = '%.3g' % mean_x
        stats['rms_x']   = '%.3g' % rms_x
        stats['mean_y']  = '%.3g' % mean_y
        stats['rms_y']   = '%.3g' % rms_y
        names_stats.append( (name, stats) )
    elif isinstance(h, ROOT.TGraph) \
            or isinstance(h, ROOT.TGraphErrors) \
            or isinstance(h, ROOT.TGraphAsymmErrors):
        if not quiet:
            print('WARNING: HighSlideRootFileIndex.get_object_stats( %s ) not implemented.' % type(h))
    elif isinstance(h, ROOT.THStack):
        stack_stats = get_object_stats( h.GetStack().Last() )
        assert len(stack_stats) == 1, type(h.GetStack().Last())
        stack_stats[0] = ('stack sum', stack_stats[0][1]) # reset name
        names_stats.extend( stack_stats )
        stack_hists_stats = []
        for hist in h.GetHists():
            stack_hists_stats.extend( get_object_stats(hist) )
        stack_hists_stats.reverse()
        names_stats.extend(stack_hists_stats)
    else:
        if not quiet:
            print('WARNING: HighSlideRootFileIndex.get_object_stats( %s ) not implemented.' % type(h))
    return names_stats

#__________________________________________________________________________
def clean_stats_names(names_stats):
    """Removes a common postfix from any of the names in the stats."""
    name = names_stats[-1][0]
    postfix = None
    sep = '__'
    if name.count(sep):
        postfix = name.split(sep)[-1]
    if postfix:
        for i in xrange(len(names_stats)):
            name, stats = names_stats[i]
            if name.endswith(sep+postfix):
                name = '__'.join(name.split(sep)[0:-1])
                names_stats[i] = (name, stats)

#__________________________________________________________________________
def convert_stats_to_table(names_stats):
    ## hack, need to come up with a way to determine which stats to expect,
    ## and how to organize the table(s)
    if 'rms_x' in names_stats[0][1]: # TH2
        top_row = ['name', 'entries', 'int', 'err', 'mean_x', 'rms_x', 'mean_y', 'rms_y']
    else:
        top_row = ['name', 'entries', 'int', 'err', 'mean', 'rms', 'under', 'over']
    tab = [top_row]
    for name, stats in names_stats:
        row = []
        for x in top_row:
            if x == 'name':
                row.append(name)
            else:
                row.append( stats.get(x, '') )
        tab.append(row)
    return tab

#__________________________________________________________________________
def convert_table_to_html(tab):
    html = ['    <table>\n']
    is_first = True
    for row in tab:
        html += ['        <tr>']
        for i_col, col in enumerate(row):
            row[i_col] = check_for_too_long_mouse_over(str(col))
        if is_first:
            for col in row:
                html += ['<th>%s</th>' % col]
            is_first = False
        else:
            for col in row:
                html += ['<td>%s</td>' % col]
        html += ['</tr>\n']
    html += ['    </table>\n']
    html = ''.join(html)
    return html

#__________________________________________________________________________
def check_for_too_long_mouse_over(s, limit=20):
    if len(s) > limit:
        return '<a title="%s" class="too_long">%s...</a>' % (s, s[:limit-3])
    return s

#______________________________________________________________________________
def walk(top, topdown=True):
    """
    os.path.walk like function for TDirectories.
    Return 4-tuple: (dirpath, dirnames, filenames, top)
        dirpath = 'file_name.root:/some/path' # may end in a '/'?
        dirnames = ['list', 'of' 'TDirectory', 'keys']
        filenames = ['list', 'of' 'object', 'keys']
        top = this level's TDirectory
    """
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    assert isinstance(top, ROOT.TDirectory)
    names = [k.GetName() for k in top.GetListOfKeys()]
    dirpath = top.GetPath()
    dirnames = []
    filenames = []
    ## filter names for directories
    for k in names:
        d = top.Get(k)
        if isinstance(d, ROOT.TDirectory):
            dirnames.append(k)
        else:
            filenames.append(k)
    ## sort
    dirnames.sort()
    filenames.sort()
    ## yield
    if topdown:
        yield dirpath, dirnames, filenames, top
    for dn in dirnames:
        d = top.Get(dn)
        for x in walk(d, topdown):
            yield x
    if not topdown:
        yield dirpath, dirnames, filenames, top

#______________________________________________________________________________
def convert_eps_to_gif(eps):
    if not quiet:
        print('converting eps to gif: ', eps)
    assert eps.endswith('.eps')
    name = eps[:-3] + 'gif'
#    os.system('convert -resize x%i -antialias -colors 64 -format gif %s %s' % (img_height, eps, name) )
#    os.system('convert -size x%i -format gif %s %s' % (img_height, eps, name) )
#    os.system('convert -format gif %s[x%i] %s' % (eps, img_height, name) )
    os.system('convert -format gif -antialias %s[x%i] %s' % (eps, img_height, name) )
    if not quiet:
        print('  Created %s' % name)
    return name

#______________________________________________________________________________
def convert_eps_to_thumb_gif(eps):
    if not quiet:
        print('converting eps to thumb gif: ', eps)
    assert eps.endswith('.eps')
    name = eps[:-3] + 'thumb.gif'
#    os.system('convert -resize x%i -antialias -colors 64 -format gif %s %s' % (thumb_height, eps, name) )
    os.system('convert -format gif -antialias %s[x%i] %s' % (eps, thumb_height, name) )
    if not quiet:
        print('  Created %s' % name)
    return name

#______________________________________________________________________________
def convert_eps_to_png(eps):
    if not quiet:
        print('converting eps to png: ', eps)
    assert eps.endswith('.eps')
    name = eps[:-3] + 'png'
    os.system('convert -resize x%i -antialias -colors 64 -format png %s %s' % (img_height, eps, name) )
    if not quiet:
        print('  Created %s' % name)
    return name

#______________________________________________________________________________
def convert_eps_to_thumb_png(eps):
    if not quiet:
        print('converting eps to thumb png: ', eps)
    assert eps.endswith('.eps')
    name = eps[:-3] + 'thumb.png'
    os.system('convert -resize x%i -antialias -colors 64 -format png %s %s' % (thumb_height, eps, name) )
    if not quiet:
        print('  Created %s' % name)
    return name

#______________________________________________________________________________
def strip_root_ext(path):
    reo = re.match('(\S*?)(\.canv)?(\.root)(\.\d*)?', path)
    assert reo
    return reo.group(1)

#______________________________________________________________________________
def make_dir_if_needed(path):
    if path.count('/'):
        dirname = os.path.split(path)[0]
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

#______________________________________________________________________________
def relpath(path, start='.'):
    """
    Return a relative version of a path
    Stolen implementation from Python 2.6.5 so I can use it in 2.5
    http://svn.python.org/view/python/tags/r265/Lib/posixpath.py?revision=79064&view=markup
    """
    # strings representing various path-related bits and pieces
    curdir = '.'
    pardir = '..'
    extsep = '.'
    sep = '/'
    pathsep = ':'
    defpath = ':/bin:/usr/bin'
    altsep = None
    devnull = '/dev/null'

    if not path:
        raise ValueError("no path specified")

    start_list = os.path.abspath(start).split(sep)
    path_list = os.path.abspath(path).split(sep)

    # Work out how much of the filepath is shared by start and path.
    i = len(os.path.commonprefix([start_list, path_list]))

    rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return '.'
    return os.path.join(*rel_list)


#______________________________________________________________________________
if __name__ == '__main__': main(sys.argv[1:])
