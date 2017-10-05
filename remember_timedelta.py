from datetime import datetime, timedelta


# Just for the next time I have problems with this
# Cos in a subfunction it don't seem to let you append to it, so this might be needed

day=datetime(2001,2,3,15,30)                    # Datetime eats ints, poor ints
a=[]
a.append(day.strftime("%Y-%m-%d %H:%M"))        # To string from datetime, cheat with http://strftime.org/
b=datetime.strptime(a,("%Y-%m-%d %H:%M"))       # Back to datetime from string