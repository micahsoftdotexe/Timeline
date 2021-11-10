function checkLogin() {
    $.ajax({
        type : 'GET',
        url: 'http://10.10.2.2:5000/check-login',
        success: function(data){
            console.log(data)
            return data.data.data
        }
    })
}
function login(username, password) {
    $.ajax({
        type : 'POST',
        url: 'http://10.10.2.2:5000/login',
        data: {
            'username' : username,
            'password' : password,
        },
        success: function(data){
            return true
        },
        error: function(xhr, status, error){
            console.log(xhr)
            console.log(status)
            console.log(error)
            return false
        }
    })
}