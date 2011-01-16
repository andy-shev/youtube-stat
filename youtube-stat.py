#!/usr/bin/python -tt
# -*- coding: UTF-8 -*-
# vim: ts=4 sw=4 et ai si

"""
Gather statistics of uploaded video by given user.
"""

__author__ = "Andy Shevchenko <andy.shevchenko@gmail.com>"
__license__ = "GPLv2"

import os
import sys
import dateutil.parser
import datetime
import Gnuplot
import operator
from optparse import OptionParser

import gdata.youtube.service

def parse_video_entry(entry):
    """Parse video entry - retrive necessary fields."""
    return {
        'title'     : entry.media.title.text,
        'date'      : dateutil.parser.parse(entry.published.text),
        'desc'      : entry.media.description.text,
        'view count': int(entry.statistics.view_count),
    }

def parse_video_feed(feed):
    """Parse video feed."""
    data = {}
    for entry in feed.entry:
        data[entry.id.text] = parse_video_entry(entry)
    return data

def get_user_uploads(username, version=2):
    """Get user's uploads and gather necessary data."""
    service = gdata.youtube.service.YouTubeService()
    base_uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?v=%d' % (username, version)
    data = {}
    start_index = 1
    max_results = 50
    while True:
        uri = '%s&start-index=%d&max-results=%d' % (base_uri, start_index, max_results)
        feed = service.GetYouTubeVideoFeed(uri)
        entry_data = parse_video_feed(feed)
        if entry_data:
            data.update(entry_data)
            if len(entry_data) == max_results:
                start_index += max_results
                continue
        break
    return data

def print_video_feed(data, outfile="-"):
    """Print short description of each entry."""
    if outfile == '-':
        fd = sys.stdout
    else:
        fd = open(outfile, 'w')
    for id in data:
        fd.write('Video title: %(title)s\n' % data[id])
        fd.write('Video published on: %(date)s\n' % data[id])
        fd.write('Video description: %(desc)s\n' % data[id])
        fd.write('Video view count: %(view count)d\n' % data[id])
        fd.write('---\n\n')
    fd.close()

def plot_video_stat(data, outfile="-"):
    """Plot video statistics using Gnuplot."""
    gp = Gnuplot.Gnuplot()

    # Should be first command!
    gp('set terminal png')

    if outfile == '-':
        gp('set output')
    else:
        gp('set output "%s"' % outfile)

    gp.title('View count versus date of publishing')
    gp.xlabel('Date')
    gp.ylabel('View count')
    gp('set autoscale')
    gp('set xdata time')
    gp('set xtics rotate')

    timefmt = "%s"
    gp('set timefmt "%s"' % timefmt)

    xy = []
    for id in data:
        xy.append([
            id,
            int(data[id]['date'].strftime(timefmt)),
            data[id]['view count'],
        ])

    xy.sort(key=operator.itemgetter(1))

    gpdata = Gnuplot.Data([x[1] for x in xy], [y[2] for y in xy],
        using='1:2', with_='linespoints')

    gp.plot(gpdata)

def main(argv):
    """MAIN"""
    parser = OptionParser(usage='%prog [options] <youtube_user_name>')
    parser.add_option("--show", dest="show", action="store_true", default=False,
            help="show the feed entries")
    parser.add_option("--output", dest="output", default="-",
            help="save output to the FILE")
    parser.add_option("--plot", dest="plot", action="store_true", default=False,
            help="plot chart with statistics")
    parser.add_option("--plot-file", dest="plot_file", default="output.png",
            help="plot chart to the FILE")
    (opts, args) = parser.parse_args(argv)

    if len(args) == 1:
        parser.error("incorrect number of arguments")

    if not opts.show and not opts.plot:
        parser.error("no action asked (--show or --plot)")

    data = get_user_uploads(args[1])
    if opts.show:
        print_video_feed(data, opts.output)
    if opts.plot:
        plot_video_stat(data, opts.plot_file)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

