import React, { useState, useEffect } from 'react'
import logo from './logo.svg';
import './App.css';
import {checkLogin, login} from './ApiFunctions.js'
const axios = require('axios');

function LoginForm(){
  const [inputs, setInputs] = useState({});
  const [triedToLogIn, setTriedToLogIn] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const handleChange = (event) => {
    const name = event.target.name;
    const value = event.target.value;
    setInputs(values => ({...values, [name]: value}));
  }
  const handleSubmit = (event) => {
    console.log("CALLING SUBMIT")
    event.preventDefault();
    console.log(inputs);
    setTriedToLogIn(prevTriedToLogIn => !prevTriedToLogIn);
    login(inputs.username, inputs.password)

  }

  useEffect(() => {
    setIsLoggedIn(checkLogin())
  }, [triedToLogIn])

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
        <button></button>
    </form>
  )
}

function App() {
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
    return (LoginForm());
  }
  
}

export default App;
