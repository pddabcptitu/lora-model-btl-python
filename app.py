from flask import Flask, render_template, redirect, request, jsonify, session, url_for
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

user_name = ''
user_id = ''

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', user_name=user_name, user_id=user_id)

@app.route('/api/response', methods=['POST'])
def botMessage():
    data = request.get_json() 
    message = data['input']
    message = {
        'input': message
    }
    url = 'https://cb9e-35-233-140-63.ngrok-free.app'#api ngrok để gọi model từ Jupyter Notebook
    
    response = requests.post(url, json=message)
    response = response.json()['response']
    print(response)
    # response = 'dcmmm'
    return jsonify({'message': response}), 200 

@app.route('/signup', methods=['GET'])
def page_signup():
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    global user_name
    data = request.get_json()
    name = data['user']
    mail = data['mail']
    password = data['password']
    print('name', name)
    urldb = 'user.db'
    # ket noi db
    conn = sqlite3.connect(urldb)
    # tao doi tuong de thao tac voi db 
    cursor = conn.cursor()
    cursor.execute('select email from user where email = ?', (mail,))
    mails = cursor.fetchall()
    
    if mail and password and name and mail not in [mail[0] for mail in mails]:

        # session['user'] = mail
        
        print('Vao if dc ')
        cursor.execute("""
                       insert into user (name, email, password) values(?, ?, ? );
                       """, (name, mail, password))
        cursor.execute("""
                       select id from user where email = ?
                       """, (mail, ))
        user_id = cursor.fetchone()
        user_name = name
        conn.commit()
        conn.close()

        return jsonify({
            'user_id':user_id,
            'name' : name
            }), 200
    else:
        return 'Mail đã được sử dụng!', 400

@app.route('/signin', methods=['GET'])
def page_signin():
    return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin():
    global user_id, user_name
    mail = request.form['mail']
    password = request.form['password']
    print(mail, password)
    # Kết nối với cơ sở dữ liệu
    urldb = 'user.db'
    conn = sqlite3.connect(urldb)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, password FROM user WHERE email = ?', (mail,))
    user = cursor.fetchone()
    conn.close()
    print(user)

    if user is None or user[3] != password:  
        return 'Thông tin đăng nhập không chính xác!', 400
    user_id = user[0]
    user_name = user[1]
    return redirect(url_for('home'))

@app.route('/api/conversation', methods=['POST'])
def conversation():
    data = request.get_json()
    user_id = data['user_id']
    title = data['title']
    print('==========================================================',user_id, title)
    urldb = 'user.db'
    conn = sqlite3.connect(urldb)
    cursor = conn.cursor()
    try:
        print("dcmmmmm")
        cursor.execute('INSERT INTO conversation (user_id, title) VALUES (?, ?)', (user_id, title))
        conn.commit()
    except:
        pass
    cursor.execute('select conv_id from conversation where user_id = ? order by conv_id desc', (user_id, ))
    conv_id = cursor.fetchone()
    print('Conv_id: ==== ', conv_id[0]) 
    conn.close()
    
    return jsonify({
        'conv_id': conv_id[0]
        }), 200

@app.route('/api/gethistory', methods=['GET'])
def getHistory():
    global user_id, user_name
    urldb = 'user.db'
    conn = sqlite3.connect(urldb) 
    cursor = conn.cursor()
    cursor.execute('select conv_id, title from conversation where user_id = ?', (user_id,))
    data = cursor.fetchall()
    
    return jsonify({
        'data': data
    }), 200

@app.route('/api/setconversation', methods=['POST'])
def setConversation():
    data = request.get_json()
    send = data['send']
    receive = data['receive']
    conv_id = data['conv_id']
    urldb = 'user.db'
    conn = sqlite3.connect(urldb)
    cursor = conn.cursor()
    cursor.execute('insert into message (conv_id, receive, send) values(?, ?, ?)', (conv_id, receive, send))
    print("SETCONVERSION: ",conv_id, receive, send)
    conn.commit()
    conn.close()
    return jsonify({'response': 'success'}), 200

@app.route('/api/getconversation', methods=['POST'])
def getConversation():
    conv_id = request.get_json()['conv_id']
    urldb = 'user.db'
    conn = sqlite3.connect(urldb)
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT receive, send 
                   FROM conversation, user, message
                   where conversation.conv_id = ? and conversation.user_id = user.id and message.conv_id = conversation.conv_id;
                   ''', (conv_id, ))   
    messages = cursor.fetchall()
    print(*messages)
    return jsonify({
        'messages':messages
    })

if __name__ == '__main__':
    app.run(debug=True)
