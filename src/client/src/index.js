import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';


ReactDOM.render(<App/>, document.getElementById('root'));

//
//fetch(`/api/user/HELLO`).then(function(response) {
//    return response.json().then(function(json) {
//      ReactDOM.render(<App email={json.email} />, document.getElementById('root')
//      )});
//});
