from wtforms import Form, StringField, SelectField, SubmitField, RadioField

class DeviceSearchForm(Form):
    choices = [('Name', 'Name'),
               ('ID', 'ID')]
    select = SelectField('Filter By:', choices=choices)
    search = StringField('')
    submit = SubmitField('Search')

class StateSearchForm(Form):
    choices = [('Name', 'Name'),
               ('ID', 'ID')]
    select = SelectField('Filter By:', choices=choices)
    search = StringField('')
    submit = SubmitField('Search')

