#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# subtitle_downloader.py
# Description: Download the subtitle for a movie file from www.OpenSubtitles.org
#
# Copyright (C) 2012 Antonio J. Delgado Linares

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import struct, os, sys, urllib2, re, time, stat
from BeautifulSoup import BeautifulSoup #Para procesar XML
import zipfile, tempfile

DEBUG=0
#USER_AGENT="Mozilla/5.0 (X11; Linux i686; rv:5.0) Gecko/20100101 Firefox/5.0"
USER_AGENT="subtitle_downloader/1.0"
PID=os.getpid()
BINARY=os.path.basename(sys.argv[0])
OVERWRITE=False

VIDEOEXTENSIONS=(".3g2",".3gp",".3gp2",".3gpp",".60d",".ajp",".asf",".asx",".avchd",".avi",".bik",".bix",".box",".cam",".dat",".divx",".dmf",".dv",".dvr-ms",".evo",".flc",".fli",".flic",".flv",".flx",".gvi",".gvp",".h264",".m1v",".m2p",".m2ts",".m2v",".m4e",".m4v",".mjp",".mjpeg",".mjpg",".mkv",".moov",".mov",".movhd",".movie",".movx",".mp4",".mpe",".mpeg",".mpg",".mpv",".mpv2",".mxf",".nsv",".nut",".ogg",".ogm",".omf",".ps",".qt",".ram",".rm",".rmvb",".swf",".ts",".vfw",".vid",".video",".viv",".vivo",".vob",".vro",".wm",".wmv",".wmx",".wrap",".wvx",".wx",".x264",".xvid")
languages=(
("alb","Albanian"),
("ara","Arabic"),
("arm","Armenian"),
("baq","Basque"),
("ben","Bengali"),
("bos","Bosnian"),
("bre","Breton"),
("bul","Bulgarian"),
("cat","Catalan"),
("chi","Chinese"),
("hrv","Croatian"),
("cze","Czech"),
("dan","Danish"),
("dut","Dutch"),
("eng","English"),
("epo","Esperanto"),
("est","Estonian"),
("per","Farsi"),
("fin","Finnish"),
("fre","French"),
("glg","Galician"),
("geo","Georgian"),
("ger","German"),
("ell","Greek"),
("heb","Hebrew"),
("hin","Hindi"),
("hun","Hungarian"),
("ice","Icelandic"),
("ind","Indonesian"),
("ita","Italian"),
("jpn","Japanese"),
("kaz","Kazakh"),
("khm","Khmer"),
("kor","Korean"),
("lav","Latvian"),
("lit","Lithuanian"),
("ltz","Luxembourgish"),
("mac","Macedonian"),
("may","Malay"),
("mal","Malayalam"),
("mon","Mongolian"),
("nor","Norwegian"),
("oci","Occitan"),
("pol","Polish"),
("por","Portuguese"),
("pob","Portuguese-BR"),
("rum","Romanian"),
("rus","Russian"),
("scc","Serbian"),
("sin","Sinhalese"),
("slo","Slovak"),
("slv","Slovenian"),
("spa","Spanish"),
("swa","Swahili"),
("swe","Swedish"),
("syr","Syriac"),
("tgl","Tagalog"),
("tel","Telugu"),
("tha","Thai"),
("tur","Turkish"),
("ukr","Ukrainian"),
("urd","Urdu"),
("vie","Vietnamese")
);

def CheckLanguage(LANGUAGE):
	global languages
	for lang in languages:
		if lang[0] == LANGUAGE:
			return True
	return False
	
def Message(text):
	global DEBUG,PID,BINARY
	date=time.time()
	message="%s (%s) %s %s" % (BINARY,PID,date,text)
	if DEBUG > 0:
		print message

def hashFile(name): 
      try: 
                 
                longlongformat = 'q'  # long long 
                bytesize = struct.calcsize(longlongformat) 
                    
                f = open(name, "rb") 
                    
                filesize = os.path.getsize(name) 
                hash = filesize 
                    
                if filesize < 65536 * 2: 
                       return "SizeError" 
                 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                         
    
                f.seek(max(0,filesize-65536),0) 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
                f.close() 
                returnedhash =  "%016x" % hash 
                return returnedhash 
    
      except(IOError): 
                #return "IOError"
                return False

def GetURLContent(URL):
	global USER_AGENT
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', USER_AGENT)]
	try:
		furl=opener.open(URL)
	#except urllib2.URLError:
	except:
		Message("Error opening URL '%s'" % (URL))
		return False
	try:
		content=furl.read()
	except httplib.IncompleteRead:
		Message("Error while reading URL '%s'" % (URL))
		return False
	return content
	
def ProcessArguments():
	global DEBUG,OVERWRITE
	for arg in sys.argv:
		if arg=="-d":
			DEBUG=DEBUG+1
			Message("Debug level incressed")
		if arg=="-h" or arg=="--help" or arg=="-?" or arg=="/?" or arg=="/h" or arg=="/help":
			Usage()
			sys.exit(0)
		if arg=="-o":
			OVERWRITE=True
			Message("Overwriting existing files")

def Usage():
	global BINARY
	print "Usage:"
	print "%s <VIDEO_FILE> [<LANGUAGE>] [-d] [-h]"
	print "\tVIDEO_FILE\tCan be a video file or a directory containing video files"
	print "\tLANGUAGE\tA language code that www.Opensubtitles.org admits (write a wrong one or help to see the list)"
	print "\t-d\tIncrease the debug level for each -d found in the command line arguments"
	print "\t-h\tShow this help and exists"
	print "\t-o\tOverwrite existing files"
	
def IsVideoFile(FILENAME):
	global VIDEOEXTENSIONS
	for EXT in VIDEOEXTENSIONS:
		if FILENAME.find(EXT)>-1:
			return True
	return False
	
def GetSubtitle(VIDEO_FILE,LANGUAGE):
	global DEBUG
	SHASH=hashFile(VIDEO_FILE)
	VIDEO_FILE_PATH=os.path.dirname(VIDEO_FILE)
	if DEBUG:
		Message("File: %s" % (VIDEO_FILE))
		Message("Hash: %s" % (SHASH))
		Message("Video file path: '%s'" % VIDEO_FILE_PATH)

	if not SHASH or SHASH == "SizeError":
		Message("Hash: False (maybe is not a video file)")
		return 0
	URL="http://www.opensubtitles.org/en/search/sublanguageid-%s/subformat-srt/moviehash-%s/simplexml" % (LANGUAGE,SHASH)
	Message("Search query URL: '%s'" % (URL))
	SEARCH_CONTENT=GetURLContent(URL)
	if not SEARCH_CONTENT:
		Message("I couldn't download the URL '%s'" % (URL))
		return 1

	XML_CONTENT = BeautifulSoup(SEARCH_CONTENT)
	if DEBUG > 1:
		DEBUGXMLFILENAME="%s.searchresult.debug.xml" % (BINARY)
		if os.path.exists(DEBUGXMLFILENAME):
			os.unlink(DEBUGXMLFILENAME)
		DEBUGFILE=open(DEBUGXMLFILENAME,"w")
		DEBUGFILE.write(SEARCH_CONTENT)
		DEBUGFILE.close()
		os.chmod(DEBUGXMLFILENAME,stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
		Message("Search result XML file: '%s'" % (DEBUGXMLFILENAME))
		
	if XML_CONTENT.search != None:
		if XML_CONTENT.search.results != None:
			if XML_CONTENT.search.results.subtitle != None:
				if XML_CONTENT.search.results.subtitle.download != None:
					ZIP_SUBTITLE=XML_CONTENT.search.results.subtitle.download.string
				else:
					Message("The downloaded document doesn't contain the expected structure (no download section for subtitle)")
					return 4
			else:
				Message("The downloaded document doesn't contain the expected structure (no subtitle section for results)")
				return 4
		else:
			Message("Sorry, not found in www.OpenSubtitles.org")
			return 4
	else:
		Message("The downloaded document doesn't contain the expected structure (no search section)")
		return 4
	Message("URL of the (first) ZIP file containing the subtitles: '%s'" % (ZIP_SUBTITLE))

	TMPFILEO=tempfile.mkstemp(suffix='.zip', prefix='tmp', dir="/tmp/", text=False)
	TMPFILENAME=TMPFILEO[1]
	Message("Saving ZIP temporarily to '%s' (don't forget to remove it)" % (TMPFILENAME))
	TMPFILE=open(TMPFILENAME,"w")
	ZIP_SUB_DATA=GetURLContent(ZIP_SUBTITLE)
	if not ZIP_SUB_DATA:
		DEBUG=1
		Message("Error downloading ZIP with the subtitles from '%s'" % (ZIP_SUBTITLE))
		return 2

	TMPFILE.write(ZIP_SUB_DATA)
	TMPFILE.close()
	os.chmod(TMPFILENAME,stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
	ZIP_FILE=zipfile.ZipFile(TMPFILENAME,"r")
	ZIP_CONTENT_LIST=ZIP_FILE.namelist()
	SUBTITLE_FILE_NAME=""
	SECOND_OPTION=""
	for FILE in ZIP_CONTENT_LIST:
		if FILE.find(".srt")>-1:
			SUBTITLE_FILE_NAME=FILE
		if FILE.find(".txt")>-1:
			SECOND_OPTION=FILE
	if SUBTITLE_FILE_NAME == "":
		if SECOND_OPTION == "":
			Message("I couldn't find a file with .srt (or .txt) extension in '%s'" % (TMPFILENAME))
			return 3
		else:
			SUBTITLE_FILE_NAME=SECOND_OPTION
	if os.path.exists(SUBTITLE_FILE_NAME):
		Message("Already extracted the file '%s', remove it before continue. Skipping subtitles for this movie." % (SUBTITLE_FILE_NAME))
		return 5
	Message("Extracting file '%s' from '%s' to '%s'" % (SUBTITLE_FILE_NAME,TMPFILENAME,VIDEO_FILE_PATH))
	try:
		ZIP_FILE.extract(SUBTITLE_FILE_NAME,VIDEO_FILE_PATH)
	except IOError:
		Message("I/O error, check that the disk isn't full and you have permissions to write to '%s'" % VIDEO_FILE_PATH)
		return 6

	SPLITED=os.path.splitext(VIDEO_FILE)
	NEW_SUBTITLE_FILE_NAME="%s.srt" % (SPLITED[0])

	#COUNT=0
	#while os.path.exists(NEW_SUBTITLE_FILE_NAME):
	#	COUNT=COUNT+1
	#	NEW_SUBTITLE_FILE_NAME="%s.%s.srt" % (SPLITED[0],COUNT)
	if os.path.exists("%s/%s" % (VIDEO_FILE_PATH,NEW_SUBTITLE_FILE_NAME)):
		if os.path.exists("%s/%s.bak" % (VIDEO_FILE_PATH,NEW_SUBTITLE_FILE_NAME)):
			os.unlink("%s/%s.bak" % (VIDEO_FILE_PATH,NEW_SUBTITLE_FILE_NAME))
		Message("The file '%s/%s' already exists, making a backup as '%s/%s'" % (VIDEO_FILE_PATH,NEW_SUBTITLE_FILE_NAME,VIDEO_FILE_PATH,NEW_SUBTITLE_FILE_NAME))
		os.rename("%s/%s" % (VIDEO_FILE_PATH,NEW_SUBTITLE_FILE_NAME),"%s.%s.bak" % (VIDEO_FILE_PATH,NEW_SUBTITLE_FILE_NAME))
	NEW_FILE_NAME=NEW_SUBTITLE_FILE_NAME
	if VIDEO_FILE_PATH == "":
		CURRENT_FILE_NAME=SUBTITLE_FILE_NAME
	else:
		CURRENT_FILE_NAME="%s/%s" % (VIDEO_FILE_PATH,SUBTITLE_FILE_NAME)
	try:
		os.rename(CURRENT_FILE_NAME,NEW_FILE_NAME)
	except:
		Message("Unable to rename subtitle file '%s' to '%s'" % (CURRENT_FILE_NAME,NEW_FILE_NAME))
		if not os.path.exists(CURRENT_FILE_NAME):
			Message("The source file '%s' do not exists" % CURRENT_FILE_NAME)
		if os.path.exists(NEW_FILE_NAME):
			Message("The destination file '%s' already exists" % NEW_FILE_NAME)
	Message("Subtitle extracted as '%s'" % (NEW_FILE_NAME))

ProcessArguments()

if len(sys.argv)<2:
	Message("You must specify a movie file as the first argument")
	sys.exit(65)
	
if len(sys.argv)>2:
	LANGUAGE=sys.argv[2]
	Message("Language for the subtitle: '%s'" % (LANGUAGE))
	if not CheckLanguage(LANGUAGE):
		if DEBUG == 0:
			DEBUG=1
		Message("Unknow language. Here is a list of valid languages:")
		for lang in languages:
			Message("'%s' for %s" % (lang))
		sys.exit(5)
else:
	LANGUAGE="spa"

VIDEO_FILE=sys.argv[1]

if not os.path.exists(VIDEO_FILE):
	Message("File '%s' doesn't exists" % (VIDEO_FILE))
	sys.exit(65)

if os.path.isdir(VIDEO_FILE):
	VIDEODIR=VIDEO_FILE
	DIRLIST=os.listdir(VIDEODIR)
	while len(DIRLIST)>0:
		VIDEO_FILE=DIRLIST[0]
		if IsVideoFile(VIDEO_FILE):
			GetSubtitle("%s/%s" % (VIDEODIR,VIDEO_FILE),LANGUAGE)
		else:
			if os.path.isdir(VIDEO_FILE):
				for ITEM in os.listdir(VIDEO_FILE):
					DIRLIST.append("%s/%s" % (VIDEO_FILE,ITEM))
		DIRLIST.remove(VIDEO_FILE)
		
else:
	GetSubtitle(VIDEO_FILE,LANGUAGE)
