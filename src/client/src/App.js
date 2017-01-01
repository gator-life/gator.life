import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

class Actions {
  static editEmail(self) {
    fetch(`/api/user/HELLO`).then(function (response) {
      return response.json().then(function (json) {
        self.setState({email: json.email});
      })
    });
  }
}

class App extends Component {

  constructor(props, context){
    super(props, context);
    this.state = {
      email: 'No'
    };
  }

  render() {
    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h2 name="message">Welcome to React {this.state.email}</h2>
        </div>
        <p className="App-intro">
          To get started, edit <code>src/App.js</code> and save to reload.
        </p>
        <button name="editEmail-button" onClick={() => Actions.editEmail(this)} type="button">Click Me!</button>
      </div>
    );
  }

}

export default App;
