import flask
import requests
import lxml

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, session, make_response, json, request
from werkzeug.utils import redirect
from data.users import User, Assembly
from forms.user import RegisterForm
from loginform import LoginForm
from data import db_session
from bs4 import BeautifulSoup

URLS = ['https://www.citilink.ru/product/processor-amd-ryzen-5-3600-socketam4-oem-100-000000031-1151445/',
        'https://www.citilink.ru/product/videokarta-palit-nvidia-geforce-gtx-1050ti-pa-gtx1050ti-stormx-4g-4gb-401997/',
        'https://www.citilink.ru/product/materinskaya-plata-asrock-b450m-pro4-f-socketam4-amd-b450-matx-ret-1138649/',
        'https://www.citilink.ru/product/blok-pitaniya-aerocool-vx-plus-600w-600vt-120mm-chernyi-retail-vx-600-1049258/',
        'https://www.citilink.ru/product/ustroistvo-ohlazhdeniya-kuler-deepcool-gammaxx-s40-120mm-ret-776809/',
        'https://www.citilink.ru/product/modul-pamyati-kingston-hyperx-fury-hx432c16fb3k2-16-ddr4-2x-8gb-3200-d-1183642/',
        'https://www.citilink.ru/product/zhestkii-disk-wd-caviar-blue-wd10ezex-1tb-hdd-sata-iii-3-5-692114/',
        'https://www.citilink.ru/product/ssd-nakopitel-kingston-a400-sa400s37-240g-240gb-2-5-sata-iii-420251/',
        'https://www.citilink.ru/product/blok-pitaniya-aerocool-vx-plus-750w-750vt-120mm-chernyi-retail-vx-750-1049261/']

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,'
              'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/blogs.db")
login_manager = LoginManager()
login_manager.init_app(app)


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)

    return r.text


def parse():  # парсинг данных с сайта citylink. конкретно - парсятся цены на комплектующие готовых сборок пк
    price_list = {'cpu': 0, 'gpu1': 0, 'mother': 0, 'power': 0, 'fan': 0, 'ram': 0, 'hdd': 0, 'ssd': 0, 'power2': 0}
    a = []
    for i in range(9):  # 13
        html = get_html(URLS[i])

        with open('st.html', 'w', encoding='utf-8') as file:
            b = file.write(html)

        with open('st.html', 'r', encoding='utf-8') as file:
            b = file.read()

        soup = BeautifulSoup(b, 'lxml')

        ans = soup.find('div', class_='ProductPrice ProductPrice_default ProductHeader__price-default')
        a.append(ans.find('span',
                          class_='ProductHeader__price-default_current-price').text.strip() if ans != None else '???????')

    for i in range(len(price_list.keys())):
        price_list[list(price_list.keys())[i]] = a[i] if a[i] != None else '???????'
    print(price_list)

    return price_list


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# если не авторизированный пользователь пытается зайти в создание сборок или мои сборки, его перекидывает в окно
# авторизации
@login_manager.unauthorized_handler
def unauthorize():
    return redirect('/login')


@app.route('/logout')  # адрес выхода из аккаунта
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')  # адрес главного окна
def main():
    return render_template('main_window.html')


@app.route("/myassemblies", methods=['GET', 'POST'])  # адрес сборок пользователя
@login_required  # доступно только авторизированным пользователям
def myassemblies():
    session = db_session.create_session()  # взаимодействуем с базой данных
    if flask.request.method == 'POST':  # если авторизированный пользователь добавляет новую сборку
        session = db_session.create_session()
        assembly = Assembly()
        assembly.user_id = current_user.id
        assembly.cpu = request.form.get('CPU')
        assembly.cooling = request.form.get('cooling')
        assembly.motherboard = request.form.get('motherboard')
        assembly.ram = request.form.get('ram')
        assembly.videocard = request.form.get('videocard')
        assembly.HDD = request.form.get('HDD')
        assembly.SSDdisk1 = request.form.get('SSDdisk1')
        assembly.SSDdisk2 = request.form.get('SSDdisk2')
        assembly.DVDdrive = request.form.get('DVDdrive')
        assembly.Housing = request.form.get('Housing')
        assembly.PowerSupply = request.form.get('PowerSupply')
        assembly.WiFiadapter = request.form.get('WiFiadapter')
        assembly.Soundcard = request.form.get('Soundcard')
        session.add(assembly)
        session.commit()
        assemblies = session.query(User).filter(User.id == current_user.id).first().assemblies
        return render_template('myassemblies.html', myassemblies=assemblies)  # выгружаем пользователю его список
        # сборок, предварительно обновив
    else:
        assemblies = session.query(User).filter(User.id == current_user.id).first().assemblies
        print(assemblies)
        return render_template('myassemblies.html', myassemblies=assemblies)  # выгружаем пользователю его список сборок


@app.route('/assemblies')  # адрес готовых сборок сайта
def assemblies():
    res = parse()
    return render_template('assemblies.html', cpu=res['cpu'], gpu1=res['gpu1'],
                           mother=res['mother'], power=res['power'],
                           fan=res['fan'], ram=res['ram'], hdd=res['hdd'], ssd=res['ssd'],
                           power2=res['power2'])  # предварительно запарсив перекидываем цены на комплектующие готовых
    # сборок


@app.route('/create')  # адрес создания сборок
@login_required
def create_assemblies():
    with open("accessories.json", "rt", encoding="utf8") as f:  # выгружаем из json виды комплектующих
        data = json.load(f)
    cpu = data['news'][0]
    cooling = data['news'][1]
    motherboard = data['news'][2]
    ram = data['news'][3]
    videocard = data['news'][4]
    HDD = data['news'][5]
    SSDdisk1 = data['news'][6]
    SSDdisk2 = data['news'][7]
    DVDdrive = data['news'][8]
    Housing = data['news'][9]
    PowerSupply = data['news'][10]
    WiFiadapter = data['news'][11]
    Soundcard = data['news'][12]
    return render_template('create_assemblies.html', cpu=cpu, cooling=cooling, motherboard=motherboard, ram=ram,
                           videocard=videocard, HDD=HDD, SSDdisk1=SSDdisk1, SSDdisk2=SSDdisk2, DVDdrive=DVDdrive,
                           Housing=Housing, PowerSupply=PowerSupply, WiFiadapter=WiFiadapter, Soundcard=Soundcard)
    # отправляем виды комплектующих, которые будут загружены в раскрывающийся список(<select>)


@app.route('/advice')  # адрес советов по сборке пк
def advice():
    return render_template('advice.html')


@app.route('/windows')  # адрес советов по установке виндовс
def windows():
    return render_template('windows.html')


@app.route('/delete', methods=['POST'])  # адрес созданный для взаимодействия с кнопкой "Очистить" через метод Post
@login_required
def delete():
    session = db_session.create_session()
    if flask.request.method == 'POST':
        assemblies = session.query(User).get(current_user.id).assemblies
        for i in assemblies:
            session.delete(i)
        session.commit()
    return redirect('/myassemblies')
    # очищает список сборок авторизированного пользователя. сам пользователь по итогу остается на адресе /myassemblies


@app.route('/back', methods=['POST'])  # адрес созданный для взаимодействия с кнопкой "Создание сборки" через метод Post
@login_required
def back():
    return redirect('/create')
    # переходит на адрес /create


# адрес созданный для взаимодействия с кнопкой "главное меню", которая есть на каждом адресе, чтобы пользователь
# вернулся на главное окно
@app.route('/homepage', methods=['POST'])
def homepage():
    return redirect('/')


# адрес логина, в котором пользователь будет вводить свои данные от акк. тут предусмотрены проверка пароля и логина.
# в случае если пользователь ввел все верно его перенаправляет в главное меню, откуда он может приступить к созданию
# сборок
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# адрес регистрации, в котором пользователь будет регистрироваться. предусмотрены проверки на логин, схожесть паролей.
# после успешной регистрации данные пользователя заносятся в базу данных
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')
