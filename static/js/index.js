var title_his;
if(document.querySelector('.avt')){
    var user = document.querySelector('.avt').innerHTML;
    fetch('/api/gethistory',{
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        let title_conv_id = data.data;
        console.log(title_conv_id);
        console.log(typeof title_conv_id);
        for(let [conv_id, title] of title_conv_id){
            let ul = document.querySelector('.history ul');
            let li = document.createElement('li');
            li.classList.add('title_his');
            if(conv_id) {
                li.id = conv_id;
            }
            li.innerHTML = title;
            ul.insertBefore(li, ul.firstChild);
        }
    title_his = document.querySelectorAll('.title_his');
    getConversationTitle(title_his);
    })
}else{
    var user = '';
}

if(document.querySelector('.user_id')){
    var user_id = document.querySelector('.user_id').innerHTML;
}else{
    user_id = '';
}


var flag = true;

if(document.querySelector('.new_chat')){
    document.querySelector('.new_chat').addEventListener('click', (event) => {
        event.preventDefault();
        document.querySelector('.form-message').innerHTML = '';
        flag = true;
        console.log(flag);
        title_his = document.querySelectorAll('.title_his');
        getConversationTitle(title_his);

    }); 
}
document.querySelector('.form-input').addEventListener('submit', async (event) => {
    event.preventDefault();

    let textarea = document.querySelector('#input').value;
    document.querySelector('#input').value = '';
    document.querySelector('#input').style.height = '35px';
    let divNew1 = document.createElement('div');
    divNew1.classList.add('user-message');
    let pNew = document.createElement('p');
    pNew.style.maxWidth = '70%';
    pNew.innerHTML = textarea;
    divNew1.appendChild(pNew);
    let divForm = document.querySelector('.form-message');
    divForm.appendChild(divNew1);
    divForm.scrollTop = divForm.scrollHeight;
    let his_title = document.querySelector('.title_his');
    console.log('his_title', his_title);
    if(his_title){
        var conv_id = his_title.id;
        console.log('conv_id trong if his_title :', conv_id);
    }
    if(flag){
        if(user){
            console.log('user: ', user);
            let title = textarea.split(" ");
            let str = "";
            for(let i = 0; i < (5 < title.length ? 5 : title.length); i++){
                str += title[i] + " ";
            }

            await fetch('/api/conversation', {
                method:'POST',
                headers:{
                    'Content-Type':'application/json'
                },
                body: JSON.stringify({
                    'user_id': user_id,
                    'title': str
                })
            }).then(response => response.json())
            .then(data => {
                conv_id = data.conv_id;
                let ul = document.querySelector('.history ul');
                let li = document.createElement('li');
                li.classList.add('title_his');
                console.log('conv_id: ', conv_id);
                if(conv_id) {
                    li.id = conv_id;
                }
                li.innerHTML = str;
                ul.insertBefore(li, ul.firstChild);
                title_his = document.querySelectorAll('.title_his');
                getConversationTitle(title_his);

            });          
        }
        
        if(document.querySelector('h1')){
            document.querySelector('h1').setAttribute('hidden', true);
        }
    }
    flag = false;
    let divNew = document.createElement('div');
    divNew.style.width = '100%';
    divNew.style.height = window.innerHeight - divNew.getBoundingClientRect().top - 200 + 'px';
    color = ['#DAC9F7', '#E9DBF7', '#E0C3FC']
    let i = 0;
    let interval = setInterval(() => {
        divNew.style.backgroundColor = color[i++ % 2];
        divNew.style.opacity = 0.5;
        divNew.style.borderRadius = '5px';
        divNew.style.boxShadow = '1px 1px 2px rgba(DA, C9, F7, 0.4)'
    }, 500);
    divForm.appendChild(divNew);
    divForm.scrollTop = divForm.scrollHeight;
    console.log("vao post sigup");
    fetch('/api/response', {
        method: 'POST',  
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'input': textarea })
    })
    .then(response => response.json()) 
    .then(data => {
        clearInterval(interval);
        divNew.style.backgroundColor = 'white';
        divNew.style.height = 'auto';
        let message = data.message;
        if(user){
            fetch('/api/setconversation',{
                method: 'POST',
                headers:{
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'send' : textarea,
                    'receive' : message,
                    'conv_id' : conv_id
                })
            }).then(error => {
                console.log(error);
            });
        }
        divNew.classList.add('bot-message');
        let pNew = document.createElement('pre');
        pNew.style.width = '95%';
        pNew.style.whiteSpace = 'pre-wrap';
        pNew.innerHTML = message
        divNew.appendChild(pNew);
        divForm.appendChild(divNew);
        divForm.scrollTop = divForm.scrollHeight;

    })
    .catch(error => {
        console.error('Error:', error);
    });
    
});


// xử lý width thanh input 
document.getElementById('input').addEventListener('input', (evnet) => {
    let textarea = document.querySelector('.input');
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
});

// truy xuất đoạn chat khi nhấn vào his_title
function getConversationTitle(title_his){
    console.log('title_his +++: ',title_his);
    for(let i of title_his){
        i.addEventListener('click', (event) => {
            event.preventDefault();
    
            let conv_id = event.target.id;
            console.log('conv_id: target_id: ',conv_id);
            fetch('/api/getconversation', {
                method:'POST',
                headers:{
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'conv_id': conv_id
                })
            }).then(response => response.json())
            .then(data => {
                messages = data.messages;
                document.querySelector('.form-message').innerHTML = '';
                for(let [receive, send] of messages){
                    // Phần user 
                    let divNew1 = document.createElement('div');
                    divNew1.classList.add('user-message');
                    var pNew = document.createElement('p');
                    pNew.style.maxWidth = '70%';
                    pNew.innerHTML = send;
                    divNew1.appendChild(pNew);
                    let divForm = document.querySelector('.form-message');
                    divForm.appendChild(divNew1);
                    divForm.scrollTop = divForm.scrollHeight;
                    // Phần bot 
                    let divNew = document.createElement('div');
                    divNew.classList.add('bot-message');
                    var pNew = document.createElement('pre');
                    pNew.style.width = '95%';
                    pNew.style.whiteSpace = 'pre-wrap';
                    pNew.innerHTML = receive;
                    divNew.appendChild(pNew);
                    divForm.appendChild(divNew);
                    divForm.scrollTop = divForm.scrollHeight;
                }
            })
        })
    }
        
}

