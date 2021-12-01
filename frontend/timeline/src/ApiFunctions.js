const axios = require('axios');
function login(username, password) {
    axios.post('http://localhost:5000/login',{
        'username':username,
        'password':password
    })
    .then(function (response) {
      console.log(checkLogin())
      //console.log(checkLogin())
        //   if(checkLogin()) {
        //     console.log('logged in')
        //   } else {
        //     console.log('not')
        //   }
      return response
      
    })
    .catch(function (error) {
        throw(error);
    })
}
export {login}