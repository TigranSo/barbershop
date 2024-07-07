from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import Flask, render_template, url_for, redirect, flash, request, abort
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SECRET_KEY'] = 'rgreg74lp874qd14s1a56wer'
db = SQLAlchemy(app)
admin = Admin(app, template_mode='bootstrap4')
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'index'


# models
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id_user = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String, nullable=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String(20), nullable=True)

    def is_admin(self):
        return self.role == 'admin'

    def get_id(self):
        return str(self.id_user)


class Barbershop(db.Model):
    __tablename__ = 'barbershop'
    id_barbershop = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    worktime_start = db.Column(db.Time, nullable=False)
    worktime_end = db.Column(db.Time, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    namecity = db.Column(db.String, nullable=False)
    barbers = db.relationship('Barber', backref='barbershop', lazy=True)
    services = db.relationship('BarbershopService', backref='barbershop', lazy=True)


class Barber(db.Model):
    __tablename__ = 'barber'
    id_barber = db.Column(db.Integer, primary_key=True)
    id_barbershop = db.Column(db.Integer, db.ForeignKey('barbershop.id_barbershop'), nullable=False)
    last_name = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    appointments = db.relationship('Appointment', backref='barber', lazy=True)


class Service(db.Model):
    __tablename__ = 'service'
    id_service = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    barbershop_services = db.relationship('BarbershopService', backref='service', lazy=True)


class BarbershopService(db.Model):
    __tablename__ = 'barbershop_service'
    id_barbershop_service = db.Column(db.Integer, primary_key=True)
    id_barbershop = db.Column(db.Integer, db.ForeignKey('barbershop.id_barbershop'), nullable=False)
    id_service = db.Column(db.Integer, db.ForeignKey('service.id_service'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    appointment_services = db.relationship('AppointmentService', backref='barbershop_service', lazy=True)


class AppointmentService(db.Model):
    __tablename__ = 'appointment_service'
    id_appointment_service = db.Column(db.Integer, primary_key=True)
    id_barbershop_service = db.Column(db.Integer, db.ForeignKey('barbershop_service.id_barbershop_service'), nullable=False)
    id_appointment = db.Column(db.Integer, db.ForeignKey('appointment.id_appointment'), nullable=False)
    appointment_detail = db.Column(db.String, nullable=False)


class Appointment(db.Model):
    __tablename__ = 'appointment'
    id_appointment = db.Column(db.Integer, primary_key=True)
    id_barber = db.Column(db.Integer, db.ForeignKey('barber.id_barber'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    appointment_services = db.relationship('AppointmentService', backref='appointment', lazy=True)


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Barbershop, db.session))
admin.add_view(AdminView(Barber, db.session))
admin.add_view(AdminView(Service, db.session))

admin.add_view(AdminView(BarbershopService, db.session))
admin.add_view(AdminView(AppointmentService, db.session))
admin.add_view(AdminView(Appointment, db.session))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


 # admin forms
class AddBarbershopForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    image = StringField('URL изображения')
    worktime_start = TimeField('Начало работы', validators=[DataRequired()])
    worktime_end = TimeField('Конец работы', validators=[DataRequired()])
    rating = FloatField('Рейтинг', validators=[DataRequired()])
    namecity = StringField('Город', validators=[DataRequired()])
    submit = SubmitField('Добавить Барбершоп')


class AddBarberForm(FlaskForm):
    id_barbershop = SelectField('Барбершоп', coerce=int, validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    rating = FloatField('Рейтинг', validators=[DataRequired()])
    submit = SubmitField('Добавить Барбера')


class AddServiceForm(FlaskForm):
    description = StringField('Описание', validators=[DataRequired()])
    submit = SubmitField('Добавить Услугу')


class AddBarbershopServiceForm(FlaskForm):
    id_barbershop = SelectField('Барбершоп', coerce=int, validators=[DataRequired()])
    id_service = SelectField('Услуга', coerce=int, validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired()])
    submit = SubmitField('Добавить Услугу')


@app.route('/admin/add_barbershop', methods=['GET', 'POST'])
@login_required
@admin_required
def add_barbershop():
    form = AddBarbershopForm()
    if form.validate_on_submit():
        barbershop = Barbershop(
            name=form.name.data,
            image=form.image.data,
            worktime_start=form.worktime_start.data,
            worktime_end=form.worktime_end.data,
            rating=form.rating.data,
            namecity=form.namecity.data
        )
        db.session.add(barbershop)
        db.session.commit()
        flash('Барбершоп добавлен!', 'success')
        return redirect(url_for('add_barbershop'))
    
    return render_template('admin/add_barbershop.html', form=form)


@app.route('/admin/add_barber', methods=['GET', 'POST'])
@login_required
@admin_required
def add_barber():
    form = AddBarberForm()
    form.id_barbershop.choices = [(b.id_barbershop, b.name) for b in Barbershop.query.all()]
    
    if form.validate_on_submit():
        barber = Barber(
            id_barbershop=form.id_barbershop.data,
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            rating=form.rating.data
        )
        db.session.add(barber)
        db.session.commit()
        flash('Барбер добавлен!', 'success')
        return redirect(url_for('add_barber'))
    
    return render_template('admin/add_barber.html', form=form)


@app.route('/admin/add_service', methods=['GET', 'POST'])
@login_required
@admin_required
def add_service():
    form = AddServiceForm()
    if form.validate_on_submit():
        service = Service(description=form.description.data)
        db.session.add(service)
        db.session.commit()
        flash('Услуга добавлена!', 'success')
        return redirect(url_for('add_service'))
    
    return render_template('admin/add_service.html', form=form)


@app.route('/admin/add_barbershop_service', methods=['GET', 'POST'])
@login_required
@admin_required
def add_barbershop_service():
    form = AddBarbershopServiceForm()
    form.id_barbershop.choices = [(b.id_barbershop, b.name) for b in Barbershop.query.all()]
    form.id_service.choices = [(s.id_service, s.description) for s in Service.query.all()]
    
    if form.validate_on_submit():
        barbershop_service = BarbershopService(
            id_barbershop=form.id_barbershop.data,
            id_service=form.id_service.data,
            price=form.price.data
        )
        db.session.add(barbershop_service)
        db.session.commit()
        flash('Услуга для барбершопа добавлена!', 'success')
        return redirect(url_for('add_barbershop_service'))
    
    return render_template('admin/add_barbershop_service.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def handle_login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        login_user(user)
        return redirect(url_for('index'))
    else:
        flash('Войти не удалось. Пожалуйста, проверьте адрес электронной почты и пароль', 'danger')
        return redirect(url_for('index'))


def handle_register():
    email = request.form['email']
    city = request.form['city']
    password = request.form['password']
    gender = request.form['gender']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    if User.query.filter_by(email=email).first():
        flash('Адрес электронной почты уже зарегистрирован.', 'danger')
        return redirect(url_for('index'))
    new_user = User(email=email, password=password, first_name=first_name, city=city, last_name=last_name, gender=gender, role="user")
    db.session.add(new_user)
    db.session.commit()
    flash('Ваша учетная запись создана! Теперь вы можете войти в систему', 'success')
    return redirect(url_for('index'))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/complete_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def complete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.id_user != current_user.id_user:
        flash('У вас нет доступа к этой записи.', 'danger')
        return redirect(url_for('index'))
    
    appointment.status = 'выполнен'
    db.session.commit()
    flash('Запись завершена!', 'success')
    return redirect(url_for('index'))


@app.route('/rate_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def rate_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.id_user != current_user.id_user:
        flash('У вас нет доступа к этой записи.', 'danger')
        return redirect(url_for('index'))
    
    rating = request.form.get('rating')
    if rating:
        appointment.rating = int(rating)
        db.session.commit()
        flash('Спасибо за вашу оценку!', 'success')
    else:
        flash('Выберите оценку перед отправкой.', 'danger')
    
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    barbershops = Barbershop.query.all()
    last_appointment = None
    total_price = 0
    all_appointments = []
    if current_user.is_authenticated:
        all_appointments = Appointment.query.filter_by(id_user=current_user.id_user).order_by(Appointment.date.desc()).all()
        if all_appointments:
            last_appointment = all_appointments[0]
            if last_appointment:
                total_price = sum(service.barbershop_service.price for service in last_appointment.appointment_services)
                
            for appointment in all_appointments:
                appointment.total_price = sum(service.barbershop_service.price for service in appointment.appointment_services)

    if request.method == 'POST':
        if 'login' in request.form:
            return handle_login()
        elif 'register' in request.form:
            return handle_register()
    
    return render_template('index.html', barbershops=barbershops, last_appointment=last_appointment, total_price=total_price, all_appointments=all_appointments)


@app.route('/page/<int:id_barbershop>', methods=['GET', 'POST'])
def page(id_barbershop):
    barbershop = Barbershop.query.get_or_404(id_barbershop)
    barbers = Barber.query.filter_by(id_barbershop=id_barbershop).all()
    services = BarbershopService.query.filter_by(id_barbershop=id_barbershop).all()

    if request.method == 'POST':
        selected_services = request.form.getlist('services')
        selected_barber = request.form['barber']
        total_price = request.form['total_price']
        return redirect(url_for('appointment', id_barbershop=id_barbershop, barber_id=selected_barber, services=','.join(selected_services), total_price=total_price))
    
    return render_template('page.html', barbershop=barbershop, barbers=barbers, services=services)


@app.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    id_barbershop = request.args.get('id_barbershop')
    barber_id = request.args.get('barber_id')
    services = request.args.get('services').split(',')
    total_price = request.args.get('total_price')

    if request.method == 'POST':
        appointment_type = request.form['appointment_type']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        user_id = current_user.id_user
        
        appointment = Appointment(
            id_barber=barber_id,
            id_user=user_id,
            date=datetime.strptime(f"{appointment_date} {appointment_time}", '%Y-%m-%d %H:%M'),
            status='в ожидании'
        )
        db.session.add(appointment)
        db.session.commit()

        for service_id in services:
            appointment_service = AppointmentService(
                id_appointment=appointment.id_appointment,
                id_barbershop_service=int(service_id),
                appointment_detail=f"{appointment_date} {appointment_time} for {service_id}"
            )
            db.session.add(appointment_service)
        db.session.commit()
        
        flash('Запись успешно создана!', 'success')
        return redirect(url_for('index'))
    
    return render_template('appointment.html', barber_id=barber_id, services=services, total_price=total_price)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'rating_desc')
    
    if query:
        search_query = "%{}%".format(query)
        barbershops = Barbershop.query.filter(Barbershop.name.like(search_query))
    else:
        barbershops = Barbershop.query
    
    if sort_by == 'rating_asc':
        barbershops = barbershops.order_by(Barbershop.rating.asc())
    else:
        barbershops = barbershops.order_by(Barbershop.rating.desc())
    
    barbershops = barbershops.all()
    
    return render_template('search_results.html', barbershops=barbershops)

       
if __name__ == '__main__':
    app.run(debug=True)
