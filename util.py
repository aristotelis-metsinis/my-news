# συναρτήσεις για αποθήκευση λίστας λεξικών σε αρχείο csv με διαχωριστικό ';' και
# για ανάκτηση λίστας λεξικών από αρχείο csv

import csv
import random
import os.path

def csv_to_dict(fname):
    # ανακτά μια λίστα από λεξικά από ένα αρχείο csv με όνομα fname
    try:
        dl = [] # new list of dictionaries
        infile = csv.DictReader(open(fname, 'r', encoding='utf-8'), delimiter=';')
        for row in infile:
            dl.append(row)
        return [dict(x) for x in dl]
    except: return []

def dict_to_csv(dl, fname):
    # αποθηκεύει μια λίστα από λεξικά dl σε ένα αρχείο csv με όνομα fname
    try:
        with open(fname, 'w', encoding='utf-8') as fout:
            w = csv.DictWriter(fout, fieldnames=dl[0].keys(), delimiter=';')
            w.writerow(dict((x,x) for x in dl[0].keys()))
            w.writerows(dl)
        #print('saved to', fname)
        return True
    except: return False

def test(): # έλεγχος καλής λειτουργίας των παραπάνω συναρτήσεων
    klist = [x for x in 'abcdefghijklmnopq']
    dl = []
    for i in range(10):
        tempd = {}
        for k in klist:
            tempd[k] = str(random.randint(1,100))
        print(tempd)
        dl.append(tempd)
    dict_to_csv(dl, 'temp.csv') # αποθήκευση λίστας λεξικών d1 στο αρχείο temp.csv

    xl = csv_to_dict('temp.csv') # ανάκτηση από το temp.csv της λίστας λεξικών
    print('\n\n\nRetrieved data')
    for x in xl:
        print(x)
    if os.path.isfile('temp.csv'): os.remove('temp.csv') # διαγραφή προσωρινού αρχείου

if __name__ == '__main__':
    test()


