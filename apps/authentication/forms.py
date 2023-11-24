from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Email, DataRequired

# login and registration
class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])

class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])

# Settings
class SettingsForm(FlaskForm):
    username = StringField('Username',
                         id='username_edit')
    email = StringField('Email',
                      id='email_edit',
                      validators=[Email()])
    confirmPassword = PasswordField('confirmPassword',
                             id='pwd_confirm',
                             validators=[DataRequired()])
    newPassword = PasswordField('newPassword',
                            id='pwd_new')
    newPasswordConfirm = PasswordField('newPasswordConfirm',
                             id='pwd_new_confirm')

# User Profile
class ProfileForm(FlaskForm):
    profileImage = FileField('profileImageEdit',
                         id='profileImage_edit')
    oldNickname = StringField('oldNickname',
                         id='nickname_old')
    nickname = StringField('Nickname',
                         id='nickname_edit')
    newPin = PasswordField('newPin',
                            id='pin_new')
    newPinConfirm = PasswordField('newPinConfirm',
                             id='pin_new_confirm')
    accountType = BooleanField('accountType',
                             id='account_type')
