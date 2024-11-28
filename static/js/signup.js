// signup


document.querySelector('.form-signup').addEventListener('submit', (event) => {
    event.preventDefault();

    console.log("vaof dc roi ")
    user = document.querySelector('#name').value;
    let mail = document.querySelector('#mail').value;
    let password = document.querySelector('#password').value;
    console.log(user, mail, password);
    fetch('api/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'user': user,
            'mail': mail,
            'password': password
        })
    }).then(response => {
        if(response.ok){
            return response.json();
        }
    })
    .then(data => {
        window.location.href='/';
    })
    .catch(error => {
        console.error(error);
    });
});
