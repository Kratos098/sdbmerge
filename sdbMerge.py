import sys
import os
import datetime
import time
from os import listdir
from os.path import isfile, join

def writetoLog(error, errorType, mode):
    """
    writes a message to log file: /opt/SA/logs/arb.log
    
    Function arguments:
        error     (String): message to be printed to log file  
        errorType (char)  : type of message, either error or informative
        mode      (String): determines if the program should exit or not
    """
    log_path = os.path.join("/opt/SA/logs/", "arb.log")
    num = ""
    if os.stat(log_path).st_size > 0:
        with open(log_path, encoding = "ISO-8859-1") as f:
            line = ""
            for line in f:
                pass
            last_line = line
        vals = [x.strip() for x in last_line.split(",")]
        if len(vals) > 0:
            num  = vals[1]
            num = num.replace(" ", "")
            num = num.replace(",", "")
            num = str(int(num) + 1)
    else:
        num = "1000"

    logfile  = open(log_path, "a")
    tz = datetime.timezone(datetime.timedelta(hours=0), "UTC")
    d = datetime.datetime.now(tz=tz)
    err_str = d.strftime("%a %b %d %H:%M:%S %Y") + ", " + num + ", S, " + errorType + ", " + error + "\n"
    logfile.write(err_str)
    logfile.close()

    if mode == "end":
        sys.exit()

class Track:
    lines        = []
    prePassTime  = 0
    startTime    = 0
    endTime      = 0
    handoverTime = 0

    def __init__(self, lines):
        """
        initializes a Track object with prePass, start, end, and handover times
        
        Function arguments:
            lines (String[]): list containing 4 Strings signifying a track
        """
        self.lines = lines
        secondLine = (self.lines)[1].split("\"")
        thirdLine  = (self.lines)[2].split("\"")
        self.prePassTime  = self.dateToInt(secondLine[1])
        self.startTime    = self.dateToInt(secondLine[3])
        self.endTime      = self.dateToInt(secondLine[5])
        self.handoverTime = self.dateToInt(thirdLine[1])
        
    def dateToInt(self, datetime_str):
        """
        converts a given date/time String into an integer value
        
        Function arguments:
            datetime_str (String): date and time to be converted
        
        Function returns:
            int: converted value of date/time
        """
        dTL = datetime_str.split(" ")
        date_str = dTL[0].split("/")
        time_str = dTL[1].split(":")
        year   = int(date_str[2])
        month  = int(date_str[0])
        day    = int(date_str[1])
        hour   = int(time_str[0])
        minute = int(time_str[1])
        second = int(time_str[2])
        dt = datetime.datetime(year, month, day, hour, minute, second)
        return int(round(dt.timestamp() * 1000))
    
class Schedule:
    fileName  = ""
    action    = ""
    header    = []
    trackList = []

    def __init__(self, fN):
        self.fileName = fN
        self.trackList = []
        self.header = []
        count = 0
        with open(self.fileName, "r") as file:
            for line in file:
                if count <= 6:
                    (self.header).append(line)
                    count += 1
                if count == 7:
                    break
        firstLine = (self.header)[0]
        if firstLine.find("Action=") == -1 or firstLine.find("ADD") != -1:
            self.action = "ADD"
        elif firstLine.find("PURGE") != -1:
            self.action = "PURGE"
        
    def addTrack(self, track):
        """
        appends a given Track, track, to the list of Tracks associated with the Schedule
        
        Function arguments:
            track (Track): a Track object to be appended to trackList
        """
        (self.trackList).append(track)
    
    def sortTracks(self):
        """
        sorts the Tracks in the list of Tracks called trackList according to startTime
        """
        (self.trackList).sort(key=lambda x: x.startTime)

if __name__ == "__main__":
    mypath = "/opt/SA/sdb/Schedule"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    if len(sys.argv) != 3:
        writetoLog("Incorrect number of arguments, need names of old and new SDB files", "E", "end")
    
    if not os.path.exists(sys.argv[1]) or not os.path.exists(sys.argv[2]):
        writetoLog("Could not find one or both schedule files, check spelling. file 1: " + sys.argv[1] + " file 2: " + sys.argv[2], "E", "end")
    writetoLog("Files are: " + sys.argv[1] + " " + sys.argv[2], "I", "continue")
    
    originalFile = Schedule(sys.argv[1]) 
    uploadedFile = Schedule(sys.argv[2])
 
    with open(uploadedFile.fileName, "r") as file:
        count = 0
        onTrack = False
        header = []
        lines = []
        for line in file:
            if line.find("</Track>") != -1:
                lines.append(line)
                uploadedFile.addTrack(Track(lines))
                lines = []
                onTrack = False
            if (line.find("<!--") != -1 or onTrack == True) and count > 2:
                lines.append(line)
                onTrack = True
            count += 1
    uploadedFile.sortTracks()

    schedule = os.path.join("/opt/SA/sdb/", "schedule")
    if uploadedFile.action == "PURGE":
        with open(schedule, "w+") as file:
            for line in uploadedFile.header:
                file.write(line)
            for track in uploadedFile.trackList:
                for line in track.lines:
                    file.write(line)
        # writetoLog("Successfully wrote to new schedule file using action PURGE", "I", "end")
        print("Successfully wrote to new schedule file using action PURGE", "I", "end")
        sys.exit()
    
    with open(originalFile.fileName, "r") as file:
        count = 0
        onTrack = False
        header = []
        lines = []
        for line in file:
            if line.find("</Track>") != -1:
                lines.append(line)
                originalFile.addTrack(Track(lines))
                lines = []
                onTrack = False
            if (line.find("<!--") != -1 or onTrack == True) and count > 6:
                lines.append(line)
                onTrack = True
            count += 1
    originalFile.sortTracks()

    with open(schedule, "w+") as file:
        for line in uploadedFile.header:
            file.write(line)
        firstStartTime = (uploadedFile.trackList[0]).startTime
        for track in originalFile.trackList:
            if track.startTime < firstStartTime:
                for line in track.lines:
                    file.write(line)
            else:
                break
        for track in uploadedFile.trackList:
            for line in track.lines:
                file.write(line)
    
    # writetoLog("Successfully wrote to new schedule file using action ADD", "I", "end")
    print("Successfully wrote to new schedule file using action ADD", "I", "end")
    sys.exit()