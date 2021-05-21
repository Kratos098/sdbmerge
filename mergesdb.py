import sys
import os
from os import path

def findAction(line):
    index = line.find("Action")
    if index == -1:
        return "ADD"
    
    index += 8
    action = ""
    while line[index] != "\"":
        action += line[index]
        index += 1
    
    return action

if __name__ == "__main__":
    # print(len(sys.argv))
    if len(sys.argv) != 3:
        print("Incorrect number of arguments.")
        sys.exit()
    
    # C:\Users\manishankar.bhaskara\Documents\Arbitrator\Arbitrator\Original files\scheduleORIG
    # C:\Users\manishankar.bhaskara\Documents\Arbitrator\Arbitrator\SDB File Manipulation\scheduleNEW
    original = sys.argv[1]
    uploaded = sys.argv[2]
    # print(original, uploaded)

    if (not path.exists(original)) or (not path.exists(uploaded)):
        print("One or both schedule files could not be found.")
        sys.exit()
    
    uploaded_lines = []
    line_number = 1
    with open(uploaded, "r") as file:
        for line in file:
            uploaded_lines.append(line)
            if line_number == 1:
                action = findAction(line)
                line_number += 1
    print(action)

    if action == "PURGE":
        with open("schedule", "w+") as file:
            for line in uploaded_lines:
                file.write(line)
        sys.exit()

    original_lines = []
    with open(original, "r") as file:
        for line in file:
            original_lines.append(line)