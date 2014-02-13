import sys
import os
import os.path
import re
import datetime 


"""
data structure:
    {
        "project1": [
            { "day": "mon", "start": "10:00", "end": "11:00", "comment": "doing a thing" },
            ...
        ],
        ...
    }
"""

class DoingEngine:
    def __init__(self):
        self.DOING = {}

    def parse_doing(self,filename):
        try:
            fh = open(filename, "r")
        except:
            return {}

        projectname = None
        linenumber = 0

        for line in fh:
            linenumber += 1
            line = line.strip()

            if line == "":
                continue

            if line[0] == "#":
                continue

            if re.match("([a-z0-9_ -]+):$", line, re.IGNORECASE):
                projectname = line[:-1].lower()
                if not projectname in self.DOING:
                    print "Found new project %s" % projectname
                    self.DOING[projectname] = []
                continue
            
            matches = re.match("(?P<day>mon|tue|wed|thu|fri) (?P<start>\d{2}:\d{2})-(?P<end>\d{2}:\d{2})(?P<comment> .+)?", line, re.IGNORECASE)
            if matches:
                if projectname is None:
                    print "Malformed file at line %d - no project name yet" % linenumber
                    continue
                if not matches.group("comment") is None:
                    comment = matches.group("comment").strip()
                else:
                    comment = ""
                self.DOING[projectname].append({"day": matches.group("day"), "start": matches.group("start"), "end": matches.group("end"), "comment": comment})
                continue

            print "NFI at line %d" % linenumber

        fh.close()

    def save_doing(self, filename):
        fh = open(filename, "w")

        for projectname in self.DOING.iterkeys():
            fh.write("%s:\n" % projectname)
            project = self.DOING[projectname]
            for entry in self.DOING[projectname]:
                fh.write("\t%s %s-%s %s\n" % (entry["day"], entry["start"], entry["end"], entry["comment"]))
            fh.write("\n")

        fh.close()

    def datetime_from_string(self, string):
        return datetime.datetime.strptime(string, "%H:%M")

    def pivot_by_day(self):
        output = { "mon": [], "tue": [], "wed": [], "thu": [], "fri": [] }
        for projectname in self.DOING.iterkeys():
            for entry in self.DOING[projectname]:
                output[entry["day"].lower()].append({ "project": projectname, "start": entry["start"], "end": entry["end"], "comment": entry["comment"] })
        return output


    def summarise_doing(self):
        weekly_total = 0
        r = self.pivot_by_day()
        for day in ["mon", "tue", "wed", "thu", "fri"]:
            print "%s:" % day.capitalize()
            running_total = 0
            for entry in r[day]:
                start_time = self.datetime_from_string(entry["start"])
                end_time = self.datetime_from_string(entry["end"])
                duration = (end_time - start_time).seconds / 3600.0
                running_total += duration
                weekly_total += duration
                print "\t%.2fh on %s %s" % (duration, entry["project"], entry["comment"])
            print "Total time spent on %s: %.2fh" % (day, running_total)
            if running_total < 37.5:
                print "  Short by %0.2fh" % (37.5 - running_total)
            print
        print "Weekly total time: %0.2fh" % weekly_total


if __name__ == "__main__":
    d = DoingEngine()
    d.parse_doing("doing.txt")


