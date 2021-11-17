const axios = require('axios');
function checkLogin() {
    axios.get('http://localhost:5000/check-login', {
        withCredentials: true,
    })
    .then(function (response) {
      console.log(response)
      return response.data.data
      
    })
}
function login(username, password) {
    axios.post('http://localhost:5000/login',{
        'username':username,
        'password':password
    })
    .then(function (response) {
      console.log(response)
      console.log(checkLogin())
      if(checkLogin()) {
        console.log('logged in')
      } else {
        console.log('not')
      }
      return response
      
    })
    .catch(function (error) {
        throw(error);
    })
}
export {checkLogin, login}