import React, { useState, useEffect } from 'react'
import logo from './logo.svg';
import './App.css';
//import {login} from './ApiFunctions.js'
import axios from "axios"


// function LoginForm(){
  
// }

function App() {
  axios.interceptors.request.use(req => {
    console.log(`${req.method} ${req.url}`);
    console.log(req)
    // Important: request interceptors **must** return the request.
    return req;
  });
  const [triedToLogIn, setTriedToLogIn] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [inputs, setInputs] = useState({});

  async function checkLogin() {
    const result = await axios.get('http://localhost:5000/check-login', {
        withCredentials: true,
    })
    console.log("data")
    console.log(result.data.data)
    return result.data.data
  }
  async function login(username, password) {
    // axios.post('http://localhost:5000/login',{
    //     'username':username,
    //     'password':password
    // })
    // .then(function (response) {
    //   console.log("Check Login")
    //   console.log(checkLogin())
    //   //console.log(checkLogin())
    //     //   if(checkLogin()) {
    //     //     console.log('logged in')
    //     //   } else {
    //     //     console.log('not')
    //     //   }
    //   return response
      
    // })
    // .catch(function (error) {
    //     throw(error);
    // })
    const result = await axios.post('http://localhost:5000/login',{
      'username':username,
      'password':password
    })
    console.log(result)
    return result
  }

  

  useEffect(() => {
    const getLogin = async () => {
      console.log("Here")
      setIsLoggedIn(await checkLogin())
    }
    getLogin()
  }, [setIsLoggedIn, triedToLogIn])

  useEffect(() => {
    console.log("IS LOGGED IN:", isLoggedIn)
  })

  if(isLoggedIn) {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <p>
            Edit <code>src/App.js</code> and save to reload.
          </p>
          <a
            className="App-link"
            href="https://reactjs.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn React
          </a>
        </header>
      </div>
    );
  } else {
    const handleChange = (event) => {
      const name = event.target.name;
      const value = event.target.value;
      setInputs(values => ({...values, [name]: value}));
    }
    const handleSubmit = (event) => {
      console.log("CALLING SUBMIT")
      event.preventDefault();
      //console.log(inputs);
      login(inputs.username, inputs.password)
      setTriedToLogIn(prevTriedToLogIn => !prevTriedToLogIn);
    }
    return (
      <form onSubmit={handleSubmit}>
        <label>Enter your name:
        <input 
          type="text" 
          name="username" 
          value={inputs.username || ""} 
          onChange={handleChange}
        />
        </label>
        <label>Enter your password:
          <input 
            type="password"
            name="password" 
            value={inputs.password || ""} 
            onChange={handleChange}
          />
          </label>
          <button>Submit</button>
      </form>
    )
  }
  
}

export default App;
