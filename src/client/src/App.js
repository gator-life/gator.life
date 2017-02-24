import React, { Component } from 'react';
import logo from './logo.svg';
import arrowup from './chevron-with-circle-up.svg'
import arrowdown from './chevron-with-circle-down.svg'
import './App.css';

class Actions {
    static editEmail(self) {
        fetch(`/api/user/HELLO`).then(function (response) {
            return response.json().then(function (json) {
                self.setState({email: json.email});
            })
        });
    }

    static getDocuments(self) {
        fetch(`/api/documents`).then(function (response) {
            return response.json().then(function (json) {
                self.setState({email: json[0].title});
            })
        })
    }

}


class Topbar extends Component {
    render() {
        return (
            <div className="Topbar">
                <div className="Topbar-logo shadow">
                    <h1><span className="logo-green">Gator</span><span className="logo-black">.</span><span
                        className="logo-red">Life</span></h1>
                </div>
                <div className="Topbar-links">
                    <li className="Register "><a  href="default.asp">Register</a></li>
                    <li className="SignIn"><a  href="news.asp">Sign in</a></li>
                    <li className="Contact"><a  href="contact.asp">Contact us</a></li>
                    <li className="OurMission"><a  href="about.asp">Our mission</a></li>
                </div>
            </div>
        );
    }
}


class Doc extends Component {
    render() {
        return (
            <div className="Doc">

                <div className="Doc-topic-wrapper">
                    <div className="Doc-topic">
                        #{
                        this.props.topic
                    }
                    </div>
                </div>

                <div className="Doc-button-group">
                    <button className="vote-up"></button>
                    <button className="vote-down"></button>
                </div>
                <div className="Doc-link">
                    <a className="Doc-title" href={this.props.url}>{this.props.title}</a>
                        <span className="Doc-domain">
                        {this.props.domain}
                        </span>
                </div>


            </div>
        );
    }
}

class Docs extends Component {

    render() {
        return (
            <div className="Docs">
                {
                    this.props.DocsData.map(function (docData) {
                        return (
                            <Doc title={docData.title}
                                 url={docData.url}
                                 domain={docData.domain}
                                 mark={docData.mark}
                                 topic={docData.topic}
                                />
                        );
                    })
                }
            </div>
        );
    }
}


class DocData {
    constructor(title, url, domain, mark, topic) {
        this.title = title;
        this.url = url;
        this.domain = domain;
        this.mark = mark;
        this.topic = topic;
    }
}


class App extends Component {

    constructor(props, context) {
        super(props, context);
        this.state = {
            email: 'No'
        };
    }

    render() {

        var data = new DocData(
            "Proof of negation and proof by contradiction",
            "http://math.andrej.com/2010/03/29/proof-of-negation-and-proof-by-contradiction/",
            "math.andrej",
            9999,
            "unconstitutionality"
        );

        var data2 = new DocData(
            "Tournoi des Six Nations : petit succès du XV de France contre l’Ecosse (22-16)",
            "http://www.leparisien.fr/sports/rugby/tournoi-des-six-nations-petit-succes-du-xv-de-france-contre-l-ecosse-22-16-12-02-2017-6675759.php",
            "leparisien",
            78,
            "foot"
        );

        var data3 = new DocData("Leaked tape reveals Trump invited club guests to 'come along' during cabinet interviews. This is a very long title",
            "http://thehill.com/blogs/blog-briefing-room/news/320220-leaked-tape-reveals-trump-invited-club-guests-to-watch-his",
            "thehill",40,"Politics"
        );

        var data4 = new DocData("SpaceX Halts Rocket Launch 10 Seconds Before Planned Liftoff", "https://www.bloomberg.com/news/articles/2017-02-18/spacex-halts-launch-of-rocket-10-seconds-before-planned-liftoff", "bloomberg", 10, "space");


        var datas = [data3, data2, data4, data, data2, data4, data3, data,
            data3, data4, data, data2, data4, data3, data];

        return (
            <div className="App">

                <Topbar/>


                <Docs DocsData={datas}/>

                <button name="editEmail-button" onClick={() => Actions.getDocuments(this)} type="button">Click Me!</button>
            </div>
        );
    }

}

export default App;
