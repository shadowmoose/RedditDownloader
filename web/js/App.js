class App extends React.Component {
	constructor(props) {
		super(props);
		this.pages = [[<Home />, 'Home'], [<Sources />, 'Sources'], [<Settings />, 'Settings']];
		this.state = {page: 0};

		// This binding is necessary to make `this` work in the callback
		this.openPage = this.openPage.bind(this);
	}


	openPage(page){
		console.log('Switching tab:', page);
		this.setState({
			page: page
		});
	}


	render() {
		let pages = this.pages.map((p)=>{
			let idx = this.pages.indexOf(p);
			return <li className={this.state.page === idx ? 'active':'inactive'} key={idx}>
				<a onClick={this.openPage.bind(this, idx)}>{p[1]}</a>
			</li>
		});
		let eles = this.pages.map((p)=>{
			let idx = this.pages.indexOf(p);
			return <div key={idx} className={this.state.page === idx? 'content':'hidden'} >{p[0]}</div>
		});
		return (
			<div>
				<ul className="header">
					{pages}
				</ul>
				<div className="content">
					{eles}
				</div>
			</div>
		);
	}
}

ReactDOM.render(
	<App />,
	document.getElementById('root')
);