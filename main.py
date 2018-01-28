# mathesis.cup.gr : Εισαγωγή στην Python
# Τελική εργασία  : mynews
'''
H γνωστή ειδησεογραφική ιστοσελίδα in.gr διαθέτει υπηρεσία απευθείας αναφοράς ειδήσεων για
διάφορες κατηγορίες με μορφή rss (rss.in.gr). Ζητείται να κατασκευάσετε μια εφαρμογή που
ενημερώνει τον χρήστη για ειδήσεις με βάση τα ενδιαφέροντά του.
1. Κάθε χρήστης ορίζει τα θέματα που τον ενδιαφέρουν και για κάθε κατηγορία αν το επιθυμεί
ορίζει συγκεκριμένους όρους αναζήτησης.
Οι επιθυμίες των χρηστών αποθηκεύονται σε αρχείο users.csv
3. Κάθε φορά που ξεκινάει η εφαρμογή αναζητάει για τον συγκεκριμένο χρήστη νεότερες ειδήσεις
με βάση τα ενδιαφέροντά του.
4. Οι ειδήσεις εμφανίζονται αρχικά ως τίτλοι, και στη συνέχεια ο χρήστης μπορεί να επιλέξει
αυτές που επιθυμεί να δει με λεπτομέρειες.
5. Η εφαρμογή θα πρέπει να υποστηρίζει τη διαχείριση χρηστών και των προφίλ τους.
'''

__authors__ = [ "Νίκος Αβούρης", "Αριστοτέλης Μετσίνης" ] 
__contact__ = "aristotelis.metsinis@gmail.com"
__date__    = "2018/01/28"
__license__ = "MIT"
__status__  = "Production"
__version__ = "1.0.0"

import os.path
import urllib.request
import urllib.error
import re
import datetime
import util
# παρέχει πρόσβαση στη βάση των Unicode χαρακτήρων, η οποία προδιαγράφει τις
# ιδιότητες για όλους τους Unicode χαρακτήρες.
import unicodedata
# τα ονόματα βοηθητικών αρχείων
data_dir = os.getcwd() # ο φάκελος για αποθήκευση δεδομένων εφαρμογής
feeds_file = os.path.join(data_dir, 'news.csv') # αρχείο με κατηγορίες από rss feeds
users_file = os.path.join(data_dir, 'users.csv') # αρχείο με προφιλ χρηστών
WIDTH = 70  #πλάτος κειμένου είδησης
URL = "http://rss.in.gr/" # διεύθυνση ειδήσεων
# καθολική μεταβλητή
user = {} # καθολική μεταβλητή που περιέχει τα στοιχεία του συνδεδεμένου κάθε φορά χρήστη
# στη μορφή: user = {'user': 'nikos', 'areas': {'Ειδήσεις Πολιτισμός': ['Καζαντζάκη'], 'Υγεία': []}
# καθολική μεταβλητή
users = [] # καθολική μεταβλητή που περιέχει λίστα από λεξικά από το αρχείο με τα προφίλ χρηστών

# --------------------------------------------------------------------------------------------------

def login_user():
    '''
    ΕΡΩΤΗΜΑ 1
    * H συνάρτηση ζητάει από τον χρήστη το username
    * Αν ο χρήστης δεν δώσει όνομα επιστρέφει την τιμή False
    * Αν δώσει τη λέξη admin καλείται η συνάρτηση admin() διαχείρισης χρηστών
    * Aν δώσει όνομα, ελέγχει αν αυτός υπάρχει ήδη καλώντας τη συνάρτηση retrieve_user(username)
        - αν η retrieve_user() επιστρέψει True (βρέθηκε χρήστης) τότε τυπώνει ένα μήνυμα καλωσορίσματος και
        επιστρέφει την τιμή True
        - αν η retrieve_user() επιστρέψει False (δεν βρέθηκε χρήστης) τότε ρωτάει τον χρήστη αν θέλει να
        δημιουργήσει προφίλ,
            + αν ο χρήστης απαντήσει θετικά, καλείται η συνάρτηση update_user() η οποία αποθηκεύει
                                το προφίλ του χρήστη στο αρχείο users_file, και επιστρέφει True,
            + αλλιώς επιστρέφει False
    '''
	
    global users
	
    username = input( "Όνομα χρήστη : " ).strip()

    if ( not username ):
        return False
    elif not re.match( r"^\w+$", username ):
        print()
        print( "Μόνο αλφαριθμητικοί χαρακτήρες είναι επιτρεπτοί [ a-z A-Z α-ω Α-Ω 0-9 _ ]" )
        return False
    else:
        users = load_users()
        if users == False:
            return False
        
        if ( username == 'admin' ):
            admin()
        else:        
            if ( retrieve_user( username ) ):
                print( "Καλώς όρισες '{}'.".format( username ) )
                return True
            else:
                reply = input( "Θέλεις να δημιουργήσεις το προφίλ του χρήστη '{}' ( 'ΝΑΙ' για αποδοχή ) ; ".format( username ) ).strip()

                if not reply or reply[ 0 ].lower() not in 'νn':
                    return False
                else:
                    update_user()
                    return True                    

# --------------------------------------------------------------------------------------------------

def admin():
    '''
    ΕΡΩΤΗΜΑ 2. Συνάρτηση που δημιουργεί και διαγράφει χρήστες (λειτουργίες διαχειριστή).
    * Φορτώνει το αρχείο χρηστών και επαναληπτικά ρωτάει τον διαχειριστή αν θέλει να διαγράψει ή να προσθέσει χρήστες
    * Αν ο διαχειριστής διαγράψει έναν χρήστη, αυτός αφαιρείται από το αρχείο χρηστών.
    * Αν ο διαχειριστής προσθέσει ένα χρήστη, αυτός προστίθεται με κενό προφίλ στο αρχείο χρηστών.
    * Η συνάρτηση χρησιμοποιεί τις βοηθητικές συναρτήσεις του αρχείου util.py
    * Δεν επιστρέφει τιμή.
    '''

    global users
	
    modify = False
    
    while True:
        print() 
        action = input( "Για διαγραφή χρήστη '-όνομα_χρήστη' , για προσθήκη χρήστη '+όνομα_χρήστη' , <enter> για έξοδο : " ).strip()

        if not action:
            if modify:

                if users:        
                    if util.dict_to_csv( users, users_file ):
                        print()
                        print( "Το αρχείο χρηστών '{}' ανανεώθηκε και αποθηκεύτηκε επιτυχώς.".format( users_file ) )
                    else:
                        print()
                        print( "Σφάλμα κατά την αποθήκευση του αρχείου χρηστών '{}'.".format( users_file ) )
                else:
                    try:
                        with open( users_file, 'w', encoding = 'utf-8' ) as fout:
                            fout.write( "user;area;keywords\n" )
                    except:
                        print()
                        print( "Σφάλμα κατά την αποθήκευση του αρχείου χρηστών '{}'.".format( users_file ) )
                    else:
                        print()
                        print( "Το αρχείο χρηστών '{}' ανανεώθηκε και αποθηκεύτηκε επιτυχώς.".format( users_file ) )
                        
            break
        else:
            action = re.match( r"^([-+])(\w+)$", action )

            if action:
                if action.group( 1 ) == "-":
                    if retrieve_user( action.group( 2 ) ):
                        print()
                        reply = input( "Θέλεις να διαγράψεις το προφίλ του χρήστη '{}' ( 'ΝΑΙ' για αποδοχή ) ; ".format( action.group( 2 ) ) ).strip()

                        if not reply or reply[ 0 ].lower() not in 'νn':
                            continue
                        
                        users = list( filter( lambda person: person[ 'user' ] != action.group( 2 ), users ) )
                        modify = True
                        print()
                        print( "0 χρήστης '{}' διαγράφηκε.".format( action.group( 2 ) ) )
                        print( "Οι χρήστες της υπηρεσίας είναι τώρα : {}".format( list ( { person[ 'user' ] for person in users } ) ) )
                    else:
                        print()
                        print( "0 χρήστης '{}' δεν βρέθηκε.".format( action.group( 2 ) ) )
                        print( "Οι χρήστες της υπηρεσίας είναι : {}".format( list ( { person[ 'user' ] for person in users } ) ) )
                else:
                    if retrieve_user( action.group( 2 ) ):
                        print()
                        print( "0 χρήστης '{}' υπάρχει ήδη.".format( action.group( 2 ) ) )
                        print( "Οι χρήστες της υπηρεσίας είναι : {}".format( list ( { person[ 'user' ] for person in users } ) ) )
                    else:
                        users.append( {'user': action.group( 2 ), 'area': '', 'keywords': ''} )
                        modify = True
                        print()
                        print( "0 χρήστης '{}' προστέθηκε.".format( action.group( 2 ) ) )
                        print( "Οι χρήστες της υπηρεσίας είναι τώρα : {}".format( list ( { person[ 'user' ] for person in users } ) ) )
            else:
                print()
                print( "Μη αποδεκτή εντολή." )        

# --------------------------------------------------------------------------------------------------

def retrieve_user(username):
    '''
    ΕΡΩΤΗΜΑ 3
    * :param username: το όνομα χρήστη που έδωσε ο χρήστης
    * :return: True αν ο χρήστης βρέθηκε στο αρχείο users_file. Στην περίπτωση αυτή στην καθολική μεταβλητή
    user φορτώνεται το λεξικό που περιέχει τα στοιχεία του χρήστη, για παράδειγμα:
    {'user': 'nikos',
     'areas': { 'Ειδήσεις Πολιτισμός': ['Καζαντζάκη'],
                'Υγεία': []
                }
    * Προσοχή: αν ένα θέμα περιέχει πολλούς όρους, αυτοί έχουν αποθηκευτεί ως μια συμβολοσειρά με το $ ως
    διαχωριστικό. Συνεπώς πρέπει εδώ να τους διαχωρίσουμε και να τους εισάγουμε στη σχετική λίστα όρων.
    * Η συνάρτηση επιστρέφει False αν δεν υπάρχει ο χρήστης ήδη στο αρχείο users_file
    '''

    global user
	
    user_profile = list( filter( lambda person: person[ 'user' ] == username, users ) )

    if user_profile:
        user[ 'user' ] = username
            
        areas = {}
        for record in user_profile:
            if record[ 'area' ]:
                areas[ record[ 'area' ] ] = record[ 'keywords' ].split("$") if record[ 'keywords' ] else []
        user[ 'areas' ] = areas
        
        return True
    else:
        user[ 'user' ] = username
        user[ 'areas' ] = {}
        
        return False

# --------------------------------------------------------------------------------------------------

def update_user():
    '''
    ΕΡΩΤΗΜΑ 4
    H συνάρτηση αυτή αποθηκεύει το περιεχόμενο της καθολικής μεταβλητής user στο αρχείο users_file
    Προσέχουμε ώστε αν στο αρχείο users_file υπάρχουν ήδη άλλοι χρήστες αυτοί πρώτα ανακτώνται, προστίθεται
    στη συνέχεια ο χρήστης user και τέλος αποθηκεύονται όλοι οι χρήστες ξανά στο users_file.
    Επίσης προσέχουμε ώστε οι όροι αναζήτησης που υπάρχουν για κάποιο θέμα να αποθηκευτούν ως μια
    συμβολοσειρά με τον χαρακτήρα $ ως διαχωριστικό.
    Επιστρέφει None
    '''

    global users

    username = user[ 'user' ]
    
    users = list( filter( lambda person: person[ 'user' ] != username , users ) )

    if user[ 'areas' ].items():
        for area, keywords in user[ 'areas' ].items():
            users.append( { 'user' : username , 'area' : area , 'keywords' : '$'.join( keywords ) } )
    else:
        users.append( {'user': username, 'area': '', 'keywords': ''} )
        
    if util.dict_to_csv( users, users_file ):
        print()
        print( "Το προφίλ του χρήστη '{}' ανανεώθηκε και αποθηκεύτηκε επιτυχώς στο αρχείο '{}'.".format( username, users_file ) )
    else:
        print()
        print( "Σφάλμα κατά την αποθήκευση του προφίλ του χρήστη '{}' στο αρχείο '{}'.".format( username, users_file ) )

# --------------------------------------------------------------------------------------------------

def load_users():
    '''
    Η συνάρτηση φορτώνει το αρχείο χρηστών,
    επιστρέφει το λεξικό που ανακτάται ή επιστρέφει False αν το αρχείο users_file δεν υπάρχει
    '''
	
    if os.path.isfile( users_file ) :
        return util.csv_to_dict( users_file )
    else:
        print()
        print( "Δεν υπάρχει το αρχείο χρηστών '{}'.".format( users_file ) )
        return False

# --------------------------------------------------------------------------------------------------

def load_newsfeeds():
    '''
    Η συνάρτηση φορτώνει τις διευθύνσεις των rss feed urls στο λεξικό feeds από το σχετικό αρχείο
    επιστρέφει το λεξικό που ανακτάται ή επιστρέφει False αν το αρχείο feeds_file δεν υπάρχει
    '''
    if os.path.isfile(feeds_file) :
        return util.csv_to_dict(feeds_file)
    else:
        print('Δεν υπάρχει αρχείο {}'.format(feeds_file))
        return False

# --------------------------------------------------------------------------------------------------

def load_news_to_temp(feeds):
    '''
    Άνοιγμα του rss feed,
    :param feeds οι θεματικές περιοχές ειδήσεων με τις αντίστοιχες διευθύνσεις των rss feeds
    φορτώνει τα άρθρα και τα αποθηκεύει σε προσωρινό αρχείο
    '''
    count = 0
    news_items = []
    for area in user['areas']:
        print(area, ' ....', end='')
        url = [x['rss'] for x in feeds if x['title'] == area]
        if url:
            url = url[0]
            req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as response:
                html = response.read().decode()
            filename = "tempfile.rss"
            with open(filename, "w", encoding="utf-8") as p:
                p.write(html)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.readline())
        except urllib.error.URLError as e:
            print(e)
            if hasattr(e, 'reason'):  # χωρίς σύνδεση ιντερνετ
                print('Αποτυχία σύνδεσης στον server')
                print('Αιτία: ', e.reason)
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                rss = f.read().replace("\n", " ")
                items = re.findall(r"<item>(.*?)</item>", rss, re.MULTILINE | re.IGNORECASE)
                count_area_items = 0
                for item in items:
                    news_item = {}
                    title = re.findall(r"<title>(.*?)</title>", item, re.MULTILINE | re.IGNORECASE)
                    date = re.findall(r"<pubdate>(.*?)</pubdate>", item, re.MULTILINE | re.IGNORECASE)
                    if len(title) > 0:
                        title = title[0]
                    else: title = ''
                    date = format_date(date[0]) if date else ' '
                    content = re.findall(r"<description>(.*?)</description>", item, re.MULTILINE | re.IGNORECASE)
                    found = False
                    if user['areas'][area]:
                        for k in user['areas'][area]:
                            if check_keyword(k, title) or check_keyword(k, content[0]):
                                found = True
                                break
                    else: found = True
                    if found:
                        count += 1
                        count_area_items += 1
                        news_item = {'no':count, 'title': title, 'date':date, 'content': content[0]}
                        news_items.append(news_item)
                        if count> 99: break # μόνο 100 πρώτες ειδήσεις
                print(count_area_items, end= ' ,   ')
    util.dict_to_csv(news_items, 'mytemp.csv') # temporary store of news items
    print()
    return len(news_items)

# --------------------------------------------------------------------------------------------------

def print_titles():
    '''
    Η συνάρτηση αυτή τυπώνει τους τίτλους των ειδήσεων που υπάρχουν στο αρχείο mytemp.csv
    :return:
    '''
    try:
        news_items = util.csv_to_dict('mytemp.csv')
        for item in news_items:
            print(item['no'] + ' [' + item['date'] + ']\t' + item['title'])
        return True
    except FileNotFoundError:
        return False

# --------------------------------------------------------------------------------------------------

def print_news_item(item_no):
    '''
    ΕΡΩΤΗΜΑ 5.
    Να γράψετε τη συνάρτηση που τυπώνει την είδηση με αριθμό item_no που βρίσκεται αποθηκευμένη στο αρχείο
    mytemp.csv.
    Χρησιμοποιήστε την βοηθητική συνάρτηση formatted_print() για το σώμα της είδησης.
    Η συνάρτηση επιστρέφει True αν η είδηση βρέθηκε και τυπώθηκε, και False αν όχι
    '''

    try:
        news_items = util.csv_to_dict( 'mytemp.csv' )

        print()
        formatted_print( news_items[ item_no - 1 ][ 'content' ] )

        return True
    except FileNotFoundError:
        return False

# --------------------------------------------------------------------------------------------------

def format_date(date):
    # βοηθητική συνάρτηση για διαμόρφωση της ημερομηνίας της είδησης
    m_gr = 'Ιαν Φεβ Μαρ Απρ Μαϊ Ιουν Ιουλ Αυγ Σεπ Οκτ Νοε ∆εκ'.split()
    m_en = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
    d = re.findall(r"([0-9]{2}\s[A-Z][a-z]{2}\s[0-9]{4})",date, re.I)
    if d : date = d[0].split()
    #if d: date = d.group(0).split()
    if date[1] in m_en: date[1] = m_gr[m_en.index(date[1])]
    return ' '.join(date)

# --------------------------------------------------------------------------------------------------

def check_keyword(keyword, text):
    # βοηθητική συνάρτηση που αναζητάει το keyword σε μια συμβολοσειρά text. Επιστρέφει True/False αν βρεθεί ή όχι.
    tonoi = ('αά', 'εέ', 'ηή', 'ιί', 'οό', 'ύυ', 'ωώ')
    n_phrase= ''
    for c in keyword:
        char = c
        for t in tonoi:
            if c in t: char = '['+t+']'
        n_phrase += char
    pattern = r'.*'+n_phrase+r'.*'
    w =re.findall(pattern, text, re.I)
    if w:
        return True
    else:
        return False

# --------------------------------------------------------------------------------------------------

def formatted_print(st, width=WIDTH):
    # συνάρτηση που τυπώνει συμβολοσειρά st με πλάτος width χαρακτήρων
    para = st.split("\n")
    for p in para:
        st = p.split()
        out = ""
        while True:
            while len(st) > 0 and len(out+st[0]) < width :
                out = " ".join([out, st.pop(0)])
            print(out)
            out = ""
            if len(st) == 0 : break

# --------------------------------------------------------------------------------------------------

def manage_profile(feeds):
    global user
    modify = False
    while True:
        print_user_profile()
        print(WIDTH * '_')
        reply = input('Θέλετε να αλλάξετε το προφίλ σας; (Ναι για αλλαγές)').strip()
        if not reply or reply[0].lower() not in 'νn': break
        print('Αρχικά θα μπορείτε να επιλέξετε από θέματα ειδήσεων, στη συνέχεια να ορίσετε όρους αναζήτησης σε καθένα από αυτά')
        main_feeds = [x['title'] for x in feeds ]
        '''
        ΕΡΩΤΗΜΑ 6
        Επαναληπτικά ζητήστε από τον χρήστη να ορίσει τα θέματα ειδήσεων που τον ενδιαφέρουν (δέστε παράδειγμα στο βίντεο)
        '''
		
        print()
        for index, feed in enumerate( main_feeds ):
            print( "{}.\t{}".format( index + 1, feed ) )
                
        while True:
            print() 
            action = input( "Για διαγραφή θέματος '-αριθμός_θέματος' , για προσθήκη θέματος '+αριθμός_θέματος' , <enter> για να συνεχίσετε : " ).strip()

            if not action:
                break
            else:	
                action = re.findall( r"(?<!\S)[-+]\b\d+\b(?=\s|$)", action )

                if action:
                    for sub_action in action:

                        if not 1 <= int( sub_action[ 1: ] ) <= len( main_feeds ):
                            print()
                            print( "Το θέμα με αριθμό '{}' δεν βρέθηκε [ επιλογές : 1 - {} ]".format( sub_action[ 1: ], len( main_feeds ) ) )
                            continue

                        area = main_feeds[ int( sub_action[ 1: ] ) - 1 ]
                        if sub_action[ 0 ] == "-":
                            if area in user[ 'areas' ].keys():
                                print()
                                reply = input( "Θέλεις να διαγράψεις το θέμα '{}' [ #{} ] ( 'ΝΑΙ' για αποδοχή ) ; ".format( area, sub_action[ 1: ] ) ).strip()

                                if not reply or reply[ 0 ].lower() not in 'νn':
                                    continue
                                
                                del user[ 'areas' ][ area ]
                                modify = True
                                print()
                                print( "Το θέμα '{}' [ #{} ] διαγράφηκε.".format( area, sub_action[ 1: ] ) )
                                selected_main_feeds = [ area + " [ #" + str( main_feeds.index( area ) + 1 ) + " ]" for area in user[ 'areas' ].keys() ]
                                print( "Τα ορισμένα θέματα ειδήσεων είναι τώρα : {}".format( selected_main_feeds ) ) 
                            else:
                                print()
                                print( "Το θέμα '{}' [ #{} ] δεν βρέθηκε.".format( area, sub_action[ 1: ] ) )
                                selected_main_feeds = [ area + " [ #" + str( main_feeds.index( area ) + 1 ) + " ]" for area in user[ 'areas' ].keys() ]
                                print( "Τα ορισμένα θέματα ειδήσεων είναι : {}".format( selected_main_feeds ) )
                        else:
                            if area in user[ 'areas' ].keys():
                                print()
                                print( "Το θέμα '{}' [ #{} ] υπάρχει ήδη.".format( area, sub_action[ 1: ] ) )
                                selected_main_feeds = [ area + " [ #" + str( main_feeds.index( area ) + 1 ) + " ]" for area in user[ 'areas' ].keys() ]
                                print( "Τα ορισμένα θέματα ειδήσεων είναι : {}".format( selected_main_feeds ) )
                            else:
                                user[ 'areas' ][ area ] = []
                                modify = True
                                print()
                                print( "Το θέμα '{}' [ #{} ] προστέθηκε.".format( area, sub_action[ 1: ] ) )
                                selected_main_feeds = [ area + " [ #" + str( main_feeds.index( area ) + 1 ) + " ]" for area in user[ 'areas' ].keys() ]
                                print( "Τα ορισμένα θέματα ειδήσεων είναι τώρα : {}".format( selected_main_feeds ) )
                else:
                    print()
                    print( "Μη αποδεκτή εντολή." ) 
		
        print_user_profile()
        print('\nΤώρα για κάθε θέμα ειδήσεων μπορείτε να επιλέξετε όρους αναζήτησης')
        '''
        ΕΡΩΤΗΜΑ 7
        Επαναληπτικά ζητήστε από τον χρήστη για κάθε θέμα ειδήσεων που τον ενδιαφέρει να προσθέσει ή να αφαιρέσει
        όρους αναζήτησης (δέστε παράδειγμα στο βίντεο)
        '''

        for area in list( user[ 'areas' ].keys() ):
            print()
            print( "θέμα ειδήσεων '{}'".format( area ) )
            while True:
                print() 
                action = input( "Για διαγραφή όρου αναζήτησης '-όρος_αναζήτησης' , για προσθήκη όρου αναζήτησης '+όρος_αναζήτησης' , <enter> για να συνεχίσετε : " ).strip()

                if not action:
                    break
                else:	
                    action = re.findall( r"[-+]\w+\b", action )

                    if action:
                        for sub_action in action:
                            search_term = sub_action[ 1: ]
							
                            if sub_action[ 0 ] == "-":
                                if remove_accents( search_term ).upper() in map( lambda keyword : remove_accents( keyword ).upper(),
                                                                                 user[ 'areas' ][ area ] ):  
                                    print()
                                    reply = input( "Θέλεις να διαγράψεις τον όρο αναζήτησης '{}' ( 'ΝΑΙ' για αποδοχή ) ; ".format( search_term ) ).strip()

                                    if not reply or reply[ 0 ].lower() not in 'νn':
                                        continue
                                    
                                    user[ 'areas' ][ area ] = list( filter( lambda keyword : remove_accents( keyword ).upper() !=
                                                                            remove_accents( search_term ).upper(), user[ 'areas' ][ area ] ) )
                                    modify = True
                                    print()
                                    print( "Ο όρος αναζήτησης '{}' διαγράφηκε.".format( search_term ) )
                                    print( "Οι όροι αναζήτησης είναι τώρα : {}".format( user[ 'areas' ][ area ] ) )
                                else:
                                    print()
                                    print( "Ο όρος αναζήτησης '{}' δεν βρέθηκε.".format( search_term ) )
                                    print( "Οι όροι αναζήτησης είναι : {}".format( user[ 'areas' ][ area ] ) ) 
                            else:
                                if search_term in user[ 'areas' ][ area ]: 
                                    print()
                                    print( "Ο όρος αναζήτησης '{}' υπάρχει ήδη.".format( search_term ) )
                                    print( "Οι όροι αναζήτησης είναι : {}".format( user[ 'areas' ][ area ] ) )  
                                else:
                                    user[ 'areas' ][ area ].append( search_term )
                                    modify = True
                                    print()
                                    print( "Ο όρος αναζήτησης '{}' προστέθηκε.".format( search_term ) )
                                    print( "Οι όροι αναζήτησης είναι τώρα : {}".format( user[ 'areas' ][ area ] ) )
                    else:
                        print()
                        print( "Μη αποδεκτή εντολή." ) 
        
        print_user_profile()
        reply = input('\n ... Θέλετε άλλες αλλαγές στο προφίλ σας (ναι για αλλαγές))').strip()
        if not reply or reply[0].lower() != 'ν': break
    if modify: # χρησιμοποιήστε μια λογική μεταβλητή η οποία γίνεται True αν ο έγιναν αλλαγές στο προφίλ του χρήστη
        update_user()

# --------------------------------------------------------------------------------------------------

def remove_accents( input_str ):
    nfkd_form = unicodedata.normalize( 'NFKD', input_str )
    return u"".join( [ c for c in nfkd_form if not unicodedata.combining( c ) ] )

# --------------------------------------------------------------------------------------------------

def print_user_areas(li):
    print('\nΤα ενδιαφέροντά σας είναι ...', end='')
    items = False
    for item in li:
        if item in user['areas'].keys():
            print(item, end=', ')
            items = True
    if not items: print('ΚΑΝΕΝΑ ΕΝΔΙΑΦΕΡΟΝ', end='')
    print()

# --------------------------------------------------------------------------------------------------

def print_user_profile():
    print('\nΤα θέματα ειδήσεων που σας ενδιαφέρουν είναι:')
    if not user['areas']: print('KENO ΠΡΟΦΙΛ ΧΡΗΣΤΗ')
    for area in user['areas']:
        print(area)
        for keyword in user['areas'][area]:
            print('\t\t', keyword)

# --------------------------------------------------------------------------------------------------

def clear_temps():
    '''
    ΕΡΩΤΗΜΑ 8.
    Να καθαρίσετε όποια βοηθητικά αρχεία έχουν δημιουργηθεί κατά τη διάρκεια εκτέλεσης του προγράμματος
    '''

    try:
        os.remove( 'mytemp.csv' )
        os.remove( 'tempfile.rss' )
    except:
        pass

# --------------------------------------------------------------------------------------------------	

def main():
    print("Σήμερα είναι :", str(datetime.datetime.today()).split()[0])
    username = login_user()
    if username:
        feeds = load_newsfeeds()
        if feeds:
            print('To mynews πρoσφέρει προσωποποιημένες ειδήσεις από το in.gr')
            while True: # main menu
                print(WIDTH * '=')
                user_selected = input('(Π)ροφίλ ενδιαφέροντα, (Τ)ίτλοι ειδήσεων, (enter)Εξοδος\n').strip()
                if user_selected == '': # έξοδος
                    break
                elif user_selected.upper() in 'ΠP': # προφίλ
                    manage_profile(feeds) # διαχείριση του προφίλ χρήστη
                elif user_selected.upper() in 'ΤT': # παρουσίαση τίτλων ειδήσεων
                    if 'areas' in user.keys() and len(user['areas']) > 0 : # αν ο χρήστης έχει ορίσει areas
                        print_user_profile()
                        print('\nΤΕΛΕΥΤΑΙΕΣ ΕΙΔΗΣΕΙΣ ΠΟΥ ΣΑΣ ΕΝΔΙΑΦΕΡΟΥΝ...ΣΕ ΤΙΤΛΟΥΣ')
                        items_count = load_news_to_temp(feeds)  # φόρτωσε τις ειδήσεις που ενδιαφέρουν τον χρήστη
                        if items_count: # εαν υπάρχουν ειδήσεις σύμφωνα με το προφιλ του χρήστη ...
                            print_titles() # τύπωσε τους τίτλους των ειδήσεων του χρήστη
                            while True:
                                print(WIDTH * '_')
                                item_no = input('Επιλογή είδησης (1 .. {}) ή <enter> για να συνεχίσετε:'.format(items_count)).strip()
                                if item_no == '': break
                                if item_no.isdigit() and 0 < int(item_no) <= items_count:
                                    print_news_item(int(item_no))
                        else: print('Δεν υπάρχουν ειδήσεις με βάση το προφίλ ενδιαφερόντων σας ...')
                    else: print('Πρέπει πρώτα να δημιουργήσετε το προφίλ σας')
    clear_temps()
    print('\nΕυχαριστούμε')

# --------------------------------------------------------------------------------------------------
	
if __name__ == '__main__': main()

# --------------------------------------------------------------------------------------------------
