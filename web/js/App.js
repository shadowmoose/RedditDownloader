class Main extends React.Component {
	constructor(props) {
		super(props);
		this.pages = [[<Home />, 'Home'], [<Sources />, 'Sources'], [<Settings />, 'Settings']];
		this.state = {page: 0};

		// This binding is necessary to make `this` work in the callback
		this.openPage = this.openPage.bind(this);
	}


	openPage(page){
		console.log('OpenPage called.');
		console.log(page);
		this.setState({
			page: page
		});
	}


	render() {
		let pages = this.pages.map((p)=>{
			return <li className={this.state.page === this.pages.indexOf(p) ? 'active':'inactive'}>
				<a onClick={this.openPage.bind(this, this.pages.indexOf(p))}>{p[1]}</a>
			</li>
		});
		return (
			<div>
				<ul className="header">
					{pages}
				</ul>
				<div className="content">
					{this.pages[this.state.page][0]}
				</div>
			</div>
		);
	}
}

ReactDOM.render(
	<Main />,
	document.getElementById('root')
);