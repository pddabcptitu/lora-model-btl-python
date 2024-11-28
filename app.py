from flask import Flask, render_template, redirect, request, jsonify, session, url_for
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

@app.route('/')
@app.route('/home')
def home():
    if 'user' in session:
        return render_template('index.html', user=session['user']['user'], id = session['user']['id'])
    return render_template('index.html', user = '', id = '')

@app.route('/api/response', methods=['POST'])
def botMessage():
    data = request.get_json()  
    message = data['input']
    
    # =====lấy response từ jupyter notebook====
    message = {
        'input': message
    }
    url = 'https://66be-34-105-12-32.ngrok-free.app'#api ngrok để gọi model từ Jupyter Notebook
    response = requests.post(url, json=message)
    # print(response.text)
    response = response.json()['response']
    #lấy res trực tiếp trong máy
    # response = model_lora.response(message)
    print(response)
    return jsonify({'message': response}), 200 

@app.route('/signup', methods=['GET'])
def page_signup():
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data['user']
    mail = data['mail']
    password = data['password']
    print('name', name)
    print('mail', mail)
    urldb = 'user.db'
    # ket noi db
    conn = sqlite3.connect(urldb)
    # tao doi tuong de thao tac voi db 
    cursor = conn.cursor()
    cursor.execute('select email from user where email = ?', (mail,))
    mails = cursor.fetchall()
    print('mails: ', mails)
    
    if mail and password and name and mail not in [mail[0] for mail in mails]:
        print('Vao if dc ')
        cursor.execute("""
                       insert into user (name, email, password) values(?, ?, ? );
                       """, (name, mail, password))
        cursor.execute("""
                       select id from user where email = ?
                       """, (mail, ))
        user_id = cursor.fetchone()
        session.clear()
        session['user'] = {
            'user': name,
            'id': user_id
        }
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
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin():
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
    print("info: ", user)

    if user is None or user[3] != password:  
        return 'Thông tin đăng nhập không chính xác!', 400
    session.clear()
    session['user'] = {
        'user':user[1],
        'id':user[0]
    }

    return redirect(url_for('home'))

@app.route('/logout')
def Logout():
    session.clear()
    return jsonify({
        'url': (url_for('signin'))
    })

@app.route('/api/conversation', methods=['POST'])
def conversation():
    data = request.get_json()
    user_id = data['user_id']
    title = data['title']
    urldb = 'user.db'
    conn = sqlite3.connect(urldb)
    cursor = conn.cursor()
    try:
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
    if 'user' in session:
        user_id = session['user']['id']
    else:
        user_id = None
    urldb = 'user.db'
    conn = sqlite3.connect(urldb) 
    cursor = conn.cursor()
    cursor.execute('select conv_id, title from conversation where user_id = ?', (user_id,))
    data = cursor.fetchall()
    print('getHistory', data)
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
    conn.commit()
    conn.close()
    return jsonify({'response': 'success'}) , 200

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
    return jsonify({
        'messages':messages
    })

@app.route('/api/deleteconversation', methods=['POST'])
def deleteConversation():
    data = request.get_json()
    print('data', data)
    id_conv = data['conv_id']
    
    urldb = 'user.db'
    conn = sqlite3.connect(urldb)
    cursor = conn.cursor()
    cursor.execute(
        '''
        delete from conversation
        where conv_id = ?
        ''',(id_conv,)
    )
    
    cursor.execute(
        '''
        delete from message 
        where conv_id = ?
        ''',(id_conv,)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'response': 'success'}) , 200

if __name__ == '__main__':
    app.run(debug=True)