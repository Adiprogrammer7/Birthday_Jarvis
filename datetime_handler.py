from datetime import datetime

def Birthdate_parser(cdate):
    date_representation = datetime.strptime(cdate, '%Y-%m-%d').date().strftime('%d %b %Y')
    short_date = datetime.strptime(cdate, '%Y-%m-%d').date().strftime('%d %b')
    birth_day = datetime.strptime(cdate, '%Y-%m-%d').day
    birth_month = datetime.strptime(cdate, '%Y-%m-%d').month
    birth_year = datetime.strptime(cdate, '%Y-%m-%d').year
    days_from_birth = (datetime.now().date() - datetime.strptime(cdate, '%Y-%m-%d').date()).days
    age = round(days_from_birth/365)
    result = {
        'date_representation': date_representation,
        'short_date': short_date,
        'birth_day': birth_day,
        'birth_month': birth_month,
        'birth_year': birth_year,
        'age': age
    }
    return result

def Days_left(cdate):
    d_1 = datetime.now().date()
    cdate_day = datetime.strptime(cdate, '%Y-%m-%d').day
    cdate_month = datetime.strptime(cdate, '%Y-%m-%d').month
    mdate_year = datetime.now().date().year
    d_2 = datetime.strptime('{} {} {}'.format(mdate_year, cdate_month, cdate_day), '%Y %m %d').date()
    # if birthday has to be come in same year.
    if d_2 >= d_1:
        days_bet = (d_2 - d_1).days
    # if birthday has to be come in next year.(already done with current year's birthday)
    else:
        new_mdate_year = datetime.now().date().year + 1
        new_d_2 = datetime.strptime('{} {} {}'.format(new_mdate_year, cdate_month, cdate_day), '%Y %m %d').date()
        days_bet = (new_d_2 - d_1).days
    return days_bet
