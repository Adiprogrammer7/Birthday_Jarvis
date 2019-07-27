from flask import Flask, flash, redirect, render_template, request, url_for
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from wtforms import StringField, SubmitField, PasswordField
from flask_wtf import FlaskForm
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from datetime_handler import Birthdate_parser, Days_left
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# CONFIGRATIONS
app = Flask(__name__)
app.config['SECRET_KEY'] = '7dkjf0477adf747'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  #specifying our login route.
login_manager.login_message_category = 'warning'  #bootstrap class for message.

# flask_login's loader.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# DATABASE
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(20), unique= True, nullable= False)
    password = db.Column(db.String(60), nullable= False)
    dates_data = db.relationship('Birthday', backref= 'creator', lazy= True)

class Birthday(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(200), nullable= False)
    full_birthdate = db.Column(db.Integer, nullable= False)
    birthdate = db.Column(db.String(20), nullable= False)
    daysleft = db.Column(db.Integer)
    age = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)


# FORMS
class AddForm(FlaskForm):
    add_field = StringField('Add field', validators= [DataRequired()])
    add_btn = SubmitField("Add")

class EditForm(FlaskForm):
    edit_btn = SubmitField('Edit')

class RegisterForm(FlaskForm):
    register_username = StringField('Username', validators= [DataRequired(), Length(min=2, max=20)])
    register_pass = PasswordField('Password', validators= [DataRequired(), Length(min=2, max=20)])
    register_confirm_pass = PasswordField('Confirm Password', validators= [DataRequired(), EqualTo('register_pass', message='Passwords must match')])
    register_btn = SubmitField('Register')

    # custom form validation to validate 'register_username', to check if it exists already.
    def validate_register_username(self, register_username):
        user = User.query.filter_by(username= register_username.data).first()
        if user:
            raise ValidationError('Username already exists. Choose another one.')

class LoginForm(FlaskForm):
    login_username = StringField('Username', validators= [DataRequired(), Length(min=2, max=20)])
    login_pass = PasswordField('Password', validators= [DataRequired(), Length(min=2, max=20)])
    login_btn = SubmitField('Login')


# ROUTES
@app.route('/')  #whenever a new user visits the site/ a user logs out, this page will be shown.
def index():
    return render_template('index.html')
    

@app.route('/showcase', methods= ['GET', 'POST'])
@login_required  #login is required to access this page.
def showcase():
    form = AddForm()
    if request.method == 'POST':
        input_date = request.form['b_date']
        try:
            date_parser = Birthdate_parser(input_date)
            days_left = Days_left(input_date)
            # when name already exists in database.
            if Birthday.query.filter_by(name= form.add_field.data).scalar():
                flash('Name already exists in database. Try a different name.', 'warning')
                return redirect('/showcase')
            else:
                # here 'creator' is the backref used to specify User of data.
                new_entry = Birthday(name= form.add_field.data, full_birthdate= input_date, birthdate= date_parser['short_date'], daysleft= days_left, age= date_parser['age'], creator= current_user)
                db.session.add(new_entry)
                db.session.commit()
                flash('Successfully added to database!', 'success')
                return redirect('/showcase')
        except:
            flash("Something went wrong with datetime", 'danger')
            return redirect('/showcase')
    else:
        # to show data of only current user's.
        present_user = User.query.filter_by(id= current_user.get_id()).first()
        all_entries =  User.query.filter_by(username= present_user.username).first().dates_data
        return render_template('showcase.html', form= form, entries= all_entries)


@app.route('/edit/<int:id>', methods= ['GET', 'POST'])
@login_required  #login is required to access this page.
def edit(id):
    form = EditForm()
    entry_to_edit = Birthday.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # when name already exists in database.
            if Birthday.query.filter_by(name= request.form['edit_field']).scalar():
                flash('Name already exists in database. Try a different name.', 'warning')
                return redirect('/showcase')
            else:
                entry_to_edit.name = request.form['edit_field']
                entry_to_edit.birthdate = request.form['b_date']
                db.session.commit()
                flash('Entry has been updated!', 'success')
                return redirect('/showcase')
        except:
            flash('Somthing went wrong in editing data.', 'danger')
            return redirect('/showcase')
    else:
        return render_template('edit.html', form= form, entry= entry_to_edit)


@app.route('/delete/<int:id>')
@login_required  #login is required to access this page.
def delete(id):
    entry_to_delete = Birthday.query.get_or_404(id)
    try:
        db.session.delete(entry_to_delete)
        db.session.commit()
        flash("You have deleted the entry of '{}'.".format(entry_to_delete.name), 'warning')  
        return redirect('/showcase')
    except:
        flash('Something went wrong in deleting the entry.', 'danger')


@app.route('/register', methods= ['POST', 'GET'])
def register():
    # if user already logged in.
    if current_user.is_authenticated:
        flash('You are already logged in.', 'success')
        return redirect('/showcase')
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.register_pass.data).decode('utf-8')
        user = User(username= form.register_username.data, password= hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You have been registered, please login to get started!', 'success')
        return redirect('/login')
    return render_template('register.html', form= form)

@app.route('/login', methods= ['POST', 'GET'])
def login():
    # if user already logged in.
    if current_user.is_authenticated:
        flash('You are already logged in.', 'success')
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username= form.login_username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.login_pass.data):
            login_user(user, remember=False)
            return redirect('/showcase')
        else:
            flash('Login unsuccessful', 'danger')
    return render_template('login.html', form= form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run()
    