import csv

with open('eggs.csv', newline='') as csvfile:
     reader = csv.reader(csvfile, delimiter=',', quotechar='"')
     for row in reader:
        print(row)