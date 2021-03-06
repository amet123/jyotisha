#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
import os.path
import swisseph as swe
import sys
from datetime import datetime

from indic_transliteration import xsanscript as sanscript
from pytz import timezone as tz

import jyotisha
import jyotisha.custom_transliteration
import jyotisha.panchangam.temporal
from jyotisha.panchangam import scripts
from jyotisha.panchangam.spatio_temporal import City

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(asctime)s {%(filename)s:%(lineno)d}: %(message)s "
)


CODE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def writeDailyTeX(panchangam, template_file, computeLagnams=True):
    """Write out the panchangam TeX using a specified template
    """
    # day_colours = {0: 'blue', 1: 'blue', 2: 'blue',
    #                3: 'blue', 4: 'blue', 5: 'blue', 6: 'blue'}
    month = {1: 'JANUARY', 2: 'FEBRUARY', 3: 'MARCH', 4: 'APRIL',
             5: 'MAY', 6: 'JUNE', 7: 'JULY', 8: 'AUGUST', 9: 'SEPTEMBER',
             10: 'OCTOBER', 11: 'NOVEMBER', 12: 'DECEMBER'}
    WDAY = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}

    template_lines = template_file.readlines()
    for i in range(len(template_lines)):
        print(template_lines[i][:-1])

    samvatsara_id = (panchangam.year - 1568) % 60 + 1  # distance from prabhava
    samvatsara_names = (jyotisha.panchangam.temporal.NAMES['SAMVATSARA_NAMES'][panchangam.script][samvatsara_id],
                        jyotisha.panchangam.temporal.NAMES['SAMVATSARA_NAMES'][panchangam.script][(samvatsara_id % 60) + 1])

    yname = samvatsara_names[0]  # Assign year name until Mesha Sankranti

    print('\\mbox{}')
    print('\\renewcommand{\yearname}{%d}' % panchangam.year)
    print('\\begin{center}')
    print('{\\sffamily \\fontsize{80}{80}\\selectfont  %d\\\\[0.5cm]}' % panchangam.year)
    print('\\mbox{\\fontsize{48}{48}\\selectfont %s–%s}\\\\'
          % samvatsara_names)
    print('\\mbox{\\fontsize{32}{32}\\selectfont %s } %%'
          % jyotisha.custom_transliteration.tr('kali', panchangam.script))
    print('{\\sffamily \\fontsize{43}{43}\\selectfont  %d–%d\\\\[0.5cm]}\n\\hrule\n\\vspace{0.2cm}'
          % (panchangam.year + 3100, panchangam.year + 3101))
    print('{\\sffamily \\fontsize{50}{50}\\selectfont  \\uppercase{%s}\\\\[0.2cm]}' % panchangam.city.name)
    print('{\\sffamily \\fontsize{23}{23}\\selectfont  {%s}\\\\[0.2cm]}'
          % jyotisha.custom_transliteration.print_lat_lon(panchangam.city.latstr, panchangam.city.lonstr))
    print('\hrule')
    print('\end{center}')
    print('\clearpage')

    for d in range(1, jyotisha.panchangam.temporal.MAX_SZ - 1):

        [y, m, dt, t] = swe.revjul(panchangam.jd_start + d - 1)

        # checking @ 6am local - can we do any better?
        local_time = tz(panchangam.city.timezone).localize(datetime(y, m, dt, 6, 0, 0))
        # compute offset from UTC in hours
        tz_off = (datetime.utcoffset(local_time).days * 86400 +
                  datetime.utcoffset(local_time).seconds) / 3600.0

        # What is the jd at 00:00 local time today?
        jd = panchangam.jd_start - (tz_off / 24.0) + d - 1

        tithi_data_str = ''
        for tithi_ID, tithi_end_jd in panchangam.tithi_data[d]:
            # if tithi_data_str != '':
            #     tithi_data_str += '\\hspace{2ex}'
            tithi = '\\raisebox{-1pt}{\moon[scale=0.8]{%d}}\\hspace{2pt}' % (tithi_ID) + \
                    jyotisha.panchangam.temporal.NAMES['TITHI_NAMES'][panchangam.script][tithi_ID]
            if tithi_end_jd is None:
                tithi_data_str = '%s\\mbox{%s\\To{}%s}' % \
                                 (tithi_data_str, tithi, jyotisha.custom_transliteration.tr('ahOrAtram', panchangam.script))
            else:
                tithi_data_str = '%s\\mbox{%s\\To{}\\textsf{%s%s}}' % \
                                 (tithi_data_str, tithi,
                                  jyotisha.panchangam.temporal.Time(24 * (tithi_end_jd - jd)).toString(format=panchangam.fmt),
                                  '\\hspace{2ex}')

        nakshatram_data_str = ''
        for nakshatram_ID, nakshatram_end_jd in panchangam.nakshatram_data[d]:
            if nakshatram_data_str != '':
                nakshatram_data_str += '\\hspace{2ex}'
            nakshatram = jyotisha.panchangam.temporal.NAMES['NAKSHATRAM_NAMES'][panchangam.script][nakshatram_ID]
            if nakshatram_end_jd is None:
                nakshatram_data_str = '%s\\mbox{%s\\To{}%s}' % \
                                      (nakshatram_data_str, nakshatram,
                                       jyotisha.custom_transliteration.tr('ahOrAtram', panchangam.script))
            else:
                nakshatram_data_str = '%s\\mbox{%s\\To{}\\textsf{%s}}' % \
                                      (nakshatram_data_str, nakshatram,
                                       jyotisha.panchangam.temporal.Time(24 * (nakshatram_end_jd -
                                                                               jd)).toString(format=panchangam.fmt))

        rashi_data_str = ''
        for rashi_ID, rashi_end_jd in panchangam.rashi_data[d]:
            # if rashi_data_str != '':
            #     rashi_data_str += '\\hspace{2ex}'
            rashi = jyotisha.panchangam.temporal.NAMES['RASHI_NAMES'][panchangam.script][rashi_ID] + jyotisha.custom_transliteration.tr('-rAzI', panchangam.script)
            if rashi_end_jd is None:
                rashi_data_str = '%s\\mbox{%s}' % (rashi_data_str, rashi)
            else:
                rashi_data_str = '%s\\mbox{%s \\RIGHTarrow \\textsf{%s}}' % \
                                 (rashi_data_str, rashi,
                                  jyotisha.panchangam.temporal.Time(24 * (rashi_end_jd - jd)).toString(format=panchangam.fmt))
        if computeLagnams:
            lagna_data_str = 'लग्नः–'
            for lagna_ID, lagna_end_jd in panchangam.lagna_data[d]:
                lagna = jyotisha.panchangam.temporal.NAMES['RASHI_NAMES'][panchangam.script][lagna_ID]
                lagna_data_str = '%s \\mbox{%s \\RIGHTarrow \\textsf{%s}}' % \
                                 (lagna_data_str, lagna,
                                  jyotisha.panchangam.temporal.Time(24 * (lagna_end_jd - jd)).toString(format=panchangam.fmt))

        yogam_data_str = ''
        for yogam_ID, yogam_end_jd in panchangam.yogam_data[d]:
            # if yogam_data_str != '':
            #     yogam_data_str += '\\hspace{2ex}'
            yogam = jyotisha.panchangam.temporal.NAMES['YOGAM_NAMES'][panchangam.script][yogam_ID]
            if yogam_end_jd is None:
                yogam_data_str = '%s\\mbox{%s\\To{}%s}' % \
                                 (yogam_data_str, yogam, jyotisha.custom_transliteration.tr('ahOrAtram', panchangam.script))
            else:
                yogam_data_str = '%s\\mbox{%s\\To{}\\textsf{%s%s}}' % \
                                 (yogam_data_str, yogam,
                                  jyotisha.panchangam.temporal.Time(24 * (yogam_end_jd - jd)).toString(format=panchangam.fmt),
                                  '\\hspace{2ex}')

        karanam_data_str = ''
        for numKaranam, (karanam_ID, karanam_end_jd) in enumerate(panchangam.karanam_data[d]):
            # if numKaranam == 1:
            #     karanam_data_str += '\\hspace{2ex}'
            karanam = jyotisha.panchangam.temporal.NAMES['KARANAM_NAMES'][panchangam.script][karanam_ID]
            if karanam_end_jd is None:
                karanam_data_str = '%s\\mbox{%s\\To{}%s}' % \
                                   (karanam_data_str, karanam, jyotisha.custom_transliteration.tr('ahOrAtram', panchangam.script))
            else:
                karanam_data_str = '%s\\mbox{%s\\To{}\\textsf{%s%s}}' % \
                                   (karanam_data_str, karanam,
                                    jyotisha.panchangam.temporal.Time(24 * (karanam_end_jd - jd)).toString(format=panchangam.fmt),
                                    '\\hspace{2ex}')

        sunrise = jyotisha.panchangam.temporal.Time(24 * (panchangam.jd_sunrise[d] - jd)).toString(format=panchangam.fmt)
        sunset = jyotisha.panchangam.temporal.Time(24 * (panchangam.jd_sunset[d] - jd)).toString(format=panchangam.fmt)
        moonrise = jyotisha.panchangam.temporal.Time(24 * (panchangam.jd_moonrise[d] - jd)).toString(format=panchangam.fmt)
        moonset = jyotisha.panchangam.temporal.Time(24 * (panchangam.jd_moonset[d] - jd)).toString(format=panchangam.fmt)

        pratahsandhya = jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['prAtaH sandhyA'][0] -
                                                                jd)).toString(format=panchangam.fmt)
        sangava = jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['saGgava'][0] - jd)).toString(format=panchangam.fmt)
        madhyaahna = jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['madhyAhna'][0] - jd)).toString(format=panchangam.fmt)
        aparahna = jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['aparAhna'][0] - jd)).toString(format=panchangam.fmt)
        sayahna = jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['sAyAhna'][0] - jd)).toString(format=panchangam.fmt)
        sayamsandhya = jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['sAyaM sandhyA'][0] -
                                                               jd)).toString(format=panchangam.fmt)

        rahu = '%s--%s' % (
            jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['rahu'][0] - jd)).toString(format=panchangam.fmt),
            jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['rahu'][1] - jd)).toString(format=panchangam.fmt))
        yama = '%s--%s' % (
            jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['yama'][0] - jd)).toString(format=panchangam.fmt),
            jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['yama'][1] - jd)).toString(format=panchangam.fmt))
        gulika = '%s--%s' % (
            jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['gulika'][0] - jd)).toString(format=panchangam.fmt),
            jyotisha.panchangam.temporal.Time(24 * (panchangam.kaalas[d]['gulika'][1] - jd)).toString(format=panchangam.fmt))

        if panchangam.solar_month[d] == 1:
            # Flip the year name for the remaining days
            yname = samvatsara_names[1]

        print('\caldata{%s}{%s}{%s{%s}{%s}{%s}}' %
              (month[m], dt, panchangam.month_data[d],
               jyotisha.panchangam.temporal.get_chandra_masa(panchangam.lunar_month[d],
                                                             jyotisha.panchangam.temporal.NAMES, panchangam.script),
               jyotisha.panchangam.temporal.NAMES['VARA_NAMES'][panchangam.script][panchangam.weekday[d]], yname))
        print('{\\sunmoondata{%s}{%s}{%s}{%s}' % (sunrise, sunset, moonrise, moonset))
        print('{\kaalas{%s}{%s}{%s}{%s}{%s}{%s}}}' % (pratahsandhya, sangava, madhyaahna,
                                                     aparahna, sayahna, sayamsandhya,))
        if computeLagnams:
            print('{\\tnykdata{%s}%%\n{%s}{%s}%%\n{%s}%%\n{%s}{\\tiny %s}\n}'
                  % (tithi_data_str, nakshatram_data_str, rashi_data_str, yogam_data_str,
                     karanam_data_str, lagna_data_str))
        else:
            print('{\\tnykdata{%s}%%\n{%s}{%s}%%\n{%s}%%\n{%s}{\\tiny %s}\n}'
                  % (tithi_data_str, nakshatram_data_str, rashi_data_str, yogam_data_str,
                     karanam_data_str, ''))
        print('{\\rygdata{%s}{%s}{%s}}' % (rahu, yama, gulika))

        # Using set as an ugly workaround since we may have sometimes assigned the same
        # festival to the same day again!
        print('{%s}' % '\\eventsep '.join(
            [jyotisha.custom_transliteration.tr(f, panchangam.script) for f in sorted(set(panchangam.festivals[d]))]))

        print('{%s} ' % WDAY[panchangam.weekday[d]])

        if m == 12 and dt == 31:
            break

    print('\end{document}')


def main():
    [city_name, latitude, longitude, tz] = sys.argv[1:5]
    year = int(sys.argv[5])

    computeLagnams = False  # Default
    script = sanscript.DEVANAGARI  # Default script is devanagari

    if len(sys.argv) == 8:
        computeLagnams = True
        script = sys.argv[6]
    elif len(sys.argv) == 7:
        script = sys.argv[6]
        computeLagnams = False

    city = City(city_name, latitude, longitude, tz)

    panchangam = scripts.get_panchangam(city=city, year=year, script=script, computeLagnams=computeLagnams)

    panchangam.add_details()

    daily_template_file = open(os.path.join(CODE_ROOT, 'panchangam/data/templates/daily_cal_template.tex'))
    writeDailyTeX(panchangam, daily_template_file, computeLagnams)
    # panchangam.writeDebugLog()


if __name__ == '__main__':
    main()
