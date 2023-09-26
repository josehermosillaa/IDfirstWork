from datetime import datetime
from django import forms
    
MONTHS = [
            ("1", 'January'),
            ("2", 'February'),
            ("3", 'March'),
            ("4", 'April'), 
            ("5", 'May'),
            ("6", 'June'),
            ("7", 'July'),
            ("8", 'August'),
            ("9", 'September'),
            ("10", 'October'),
            ("11", 'November'),
            ("12", 'December')
            ]
YEARS = [(str(y),str(y)) for y in range(2007, datetime.now().year+1)]

class DateForm(forms.Form):
    month = forms.ChoiceField(choices=MONTHS, required=True )
    year = forms.ChoiceField( choices=YEARS ,required=True )