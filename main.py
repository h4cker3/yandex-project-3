from flask import Flask, request, render_template, redirect
from data import db_session
from data.teams import Team
from data.bases import Base
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from datetime import datetime
import json

bd_password = "SECURE"
admin_password = "314p"

base_dt = {"fish": 0,
           "oil": 0,
           "wood": 0,
           "ice": 0,
           "micro": 0,
           "jew": 0,
           "money": 1000}

base_db = {"fish": [10, 10],
           "oil": [10, 10],
           "wood": [10, 10],
           "ice": [10, 10],
           "micro": [10, 10],
           "jew": [10, 10]}


base_db1 = base_db.copy()
base_db1["jew"] = [40, 30]
base_db1["ice"] = [18, 11]
base_many_db = [base_db, base_db1]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECURE'

db_session.global_init(f"h4cker3:{bd_password}")

login_manager = LoginManager()
login_manager.init_app(app)

ROUND = 2
LAST_TIME = datetime.today()

with open('db/round.txt', 'r') as file:
    DEBUG_CODE = 2
    if DEBUG_CODE == 1 or DEBUG_CODE == 100:
        db_sess = db_session.create_session()
        for t in db_sess.query(Team).all():
            db_sess.delete(t)
        db_sess.commit()
        db_sess.close()
        db_sess = db_session.create_session()
        adm = Team(code=1, name='ADMIN TEAM', res=json.dumps(base_dt.copy()), username='admin', password='314p', orgtype='admin')
        team1 = Team()
        team1.code = 12345
        team1.name = "ЪЬЪ"
        dt = base_dt.copy()
        dt["micro"] = 100
        dt["wood"] = 13
        team1.res = json.dumps(dt)
        team1.username = 'ttt'
        team1.password = 'ttt'

        team2 = Team()
        team2.code = 54321
        team2.name = "СИГМЫ ИЗ 9Б"
        dt = base_dt.copy()
        dt["jew"] = 3
        dt["ice"] = 10000
        dt['money'] = 117117
        team2.res = json.dumps(dt)
        team2.username = 'ppp'
        team2.password = 'ppp'

        orgr = Team()
        orgr.code = 2
        orgr.name = "Полосандия"
        dt = base_dt.copy()
        orgr.res = json.dumps(dt)
        orgr.username = 'org2team'
        orgr.password = 'rest3chr'
        orgr.orgtype = 'org'
        orgr.base_id = 1

        db_sess.add(adm)
        db_sess.add(orgr)
        db_sess.add(team1)
        db_sess.add(team2)
        db_sess.commit()
        db_sess.close()
    if DEBUG_CODE == 0 or DEBUG_CODE == 100:
        db_sess = db_session.create_session()
        for t in db_sess.query(Base).all():
            db_sess.delete(t)
        db_sess.commit()
        db_sess.close()
        db_sess = db_session.create_session()
        base1 = Base(id=1, prices=json.dumps(base_many_db))
        db_sess.add(base1)
        db_sess.commit()
        db_sess.close()


@app.route("/")
@app.route("/index")
def index():
    global ROUND
    global LAST_TIME
    db_sess = db_session.create_session()
    teams_db = db_sess.query(Team).filter(Team.orgtype == "player").all()
    teams = []
    for team in teams_db:
        tres = json.loads(team.res)
        st = {'name': team.name,
        'money': tres['money'],
        'diff': sum([tres[x] for x in tres.keys()]) - tres['money']}
        teams.append(st)
    teams.sort(key=lambda x: x['money'], reverse=True)
    teams[0]['name'] = "👑 " + teams[0]['name'] + "👑"
    db_sess.close()
    if ROUND != 0:
        return render_template("index.html",
                               text=f"""Раунд игры: {ROUND}. Время, прошедшее с начала раунда: {str(datetime.today() - LAST_TIME).split('.')[0]}""", teams=teams)
    else:
        return render_template("index.html", text="""Игра еще не началась!""", teams=teams)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    usr = db_sess.query(Team).get(user_id)
    db_sess.close()
    return usr


@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect("/")


@login_required
@app.route("/team", methods=['GET'])
def team_local_page():
    team = current_user
    res = {"name": team.name,
           "id": team.id,
           "resources": json.loads(team.res)}
    if team.orgtype == 'org':
        return render_template('orgsite.html')
    return render_template('team.html', res=res, code=team.code)


@login_required
@app.route("/team", methods=['POST'])
def team_local_page_post():
    if not current_user.is_authenticated:
        return redirect("/")
    org = current_user
    if org.orgtype != 'org':
        return redirect("/")
    global ROUND
    if ROUND == 0:
        return render_template('orgsite.html', message="Игра еще не началась!", alert=True)
    code = request.form.get('code')
    res = request.form.get('res').split()[0][1:-1]
    dest = int(request.form.get('destination').split()[0][1:-1])
    amount = request.form.get('amount')
    if not amount or len(amount) == 0:
        return render_template('orgsite.html', message="Введите кол-во обменеваемого товара!", alert=True)
    if not code or len(code) == 0:
        return render_template('orgsite.html', message="Введите код команды!", alert=True)
    amount = int(amount)

    db_sess = db_session.create_session()
    team = db_sess.query(Team).filter(Team.code == code).first()
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not team:
        db_sess.close()
        return render_template('orgsite.html', message="Неверный код команды!", alert=True)  # if the user doesn't exist or password is wrong, reload the page
    # if the above check passes, then we know the user has the right credentials
    cur_db = json.loads(db_sess.query(Base).get(current_user.base_id).prices)[ROUND-1]
    price = cur_db[res][dest-1]
    dt = json.loads(team.res)
    if dest == 1:
        if dt["money"] < price*amount:
            db_sess.close()
            return render_template('orgsite.html', message=f"Команде не хватает {price*amount - dt['money']} мур-рубликов", alert=True)
        dt["money"] -= price*amount
        dt[res] += amount
    else:
        if dt[res] < amount:
            db_sess.close()
            return render_template('orgsite.html', message=f"Команде не хватает {amount - dt[res]} ресурса '{res}'", alert=True)
        dt[res] -= amount
        dt["money"] += amount*price
    team.res = json.dumps(dt)
    db_sess.commit()
    db_sess.close()
    return render_template('orgsite.html', message=f"Операция проведена успешно! ({res} {dest} {price} {amount})")


@login_required
@app.route("/team/<int:code>")
def team_page(code: int):
    if not current_user.is_authenticated:
        return redirect("/")
    db_sess = db_session.create_session()
    if current_user.orgtype != 'admin':
        return "<h1>Доступ запрещен!</h1>"
    ans = db_sess.query(Team).filter(Team.code == str(code)).all()
    if len(ans) == 0:
        return "Такой команды не существует!"
    team = ans[0]
    res = {"name": team.name,
           "id": team.id,
           "resources": json.loads(team.res)}
    db_sess.close()
    return render_template('team.html', res=res, code=team.code)


@login_required
@app.route("/api/team/<int:code>")
def team_page_api(code: int):
    if not current_user.is_authenticated:
        return redirect("/")
    db_sess = db_session.create_session()
    if current_user.orgtype != 'admin':
        return "<h1>Доступ запрещен!</h1>"
    ans = db_sess.query(Team).filter(Team.code == str(code)).all()
    if len(ans) == 0:
        return "Такой команды не существует!"
    team = ans[0]
    res = {"name": team.name,
           "id": team.id,
           "type": team.orgtype,
           "resources": json.loads(team.res)}
    if res["type"] == "org":
        res["base"] = json.loads(db_sess.query(Base).get(team.base_id).prices)
        res["base_id"] = team.base_id
    db_sess.close()
    return res



@login_required
@app.route("/round/<int:round_id>")
def start_a_round(round_id: int):
    if not current_user.is_authenticated:
        return redirect("/")
    if current_user.orgtype != 'admin':
        return "<h1>Доступ запрещен!</h1>"
    global ROUND
    global LAST_TIME
    ROUND = round_id
    LAST_TIME = datetime.today()
    return f"Раунд изменен на номер {ROUND}, время начала: {LAST_TIME.isoformat()}"


@app.route("/login", methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    username = request.form.get('username')
    password = request.form.get('password')

    db_sess = db_session.create_session()
    user = db_sess.query(Team).filter(Team.username == username).first()
    db_sess.close()
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not user.password == password:
        return redirect("/login")  # if the user doesn't exist or password is wrong, reload the page
    login_user(user)
    # if the above check passes, then we know the user has the right credentials
    return redirect('/team')


def main():
    app.run()


if __name__ == '__main__':
    main()