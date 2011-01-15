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
    uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?v=%d' % (username, version)
    return parse_video_feed(service.GetYouTubeVideoFeed(uri))

def print_video_feed(data):
    """Print short description of each entry."""
    for id in data:
        print 'Video title: %(title)s' % data[id]
        print 'Video published on: %(date)s' % data[id]
        print 'Video description: %(desc)s' % data[id]
        print 'Video view count: %(view count)d' % data[id]
        print "---\n"

def plot_video_stat(data, outfile="output.png"):
    """Plot video statistics using Gnuplot."""
    gp = Gnuplot.Gnuplot()

    gp('set terminal png')
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
    data = get_user_uploads(argv[1])
    print_video_feed(data)
    plot_video_stat(data)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

