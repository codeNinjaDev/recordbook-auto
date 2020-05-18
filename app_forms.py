from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, PasswordField, SubmitField, validators
from wtforms.widgets import TextArea

class ActivityForm(FlaskForm):
    year = IntegerField('Year', default=2020)
    importance = StringField('Importance/Responsibility', [validators.InputRequired()], widget=TextArea(), default="")

class LeadershipForm(ActivityForm):
    activity = StringField('Leadership Activity', [validators.InputRequired()], default="")
    role = SelectField(u'Role', choices=[('E', 'Elected'), ('A', 'Appointed'), ('V', 'Volunteer'), ('P', 'Promotional')], default="E")
    level = SelectField(u'Level', choices=[('Cl', 'Club'), ('Co', 'County'), ('D', 'District'), ('S', 'State'), ('N', "National")], default="Cl")
    lead_submit = SubmitField('Submit')

class ServiceForm(ActivityForm):
    activity = StringField('Service Activity', [validators.InputRequired()], default="")
    role = SelectField(u'Role', choices=[('Y', 'Yourself'), ('M', 'Member of a Group'), ('P', 'Primary Leadership')], default="Y")
    service_submit = SubmitField('Submit')

class CareerForm(ActivityForm):
    activity = StringField('Career Activity', [validators.InputRequired()], default="")
    career_submit = SubmitField('Submit')

class AwardForm(ActivityForm):
    recognition = StringField('Recognition', [validators.InputRequired()], default="")
    level = SelectField(u'Level', choices=[('Cl', 'Club'), ('Co', 'County'), ('D', 'District'), ('S', 'State'), ('N', "National")], default="Cl")
    award_submit = SubmitField('Submit')

class ProjectForm(ActivityForm):
    project_name = StringField('Project Name', [validators.InputRequired()], default="")
    activity = StringField('Activity', [validators.DataRequired()])
    hours = IntegerField('Hours')
    project_submit = SubmitField('Submit')

