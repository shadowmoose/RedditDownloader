class Main extends React.Component {
	constructor(props) {
		super(props);
		this.state = {page: <Home />};

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
		return (
			<div>
				<h1>Reddit Media Downloader</h1>
				<ul className="header">
					<li><a onClick={this.openPage.bind(this, <Home />)}>Home</a></li>
					<li><a onClick={this.openPage.bind(this, <Sources />)}>Sources</a></li>
					<li><a onClick={this.openPage.bind(this, <Account />)}>Account</a></li>
				</ul>
				<div className="content">
					{this.state.page}
				</div>
			</div>
		);
	}
}

ReactDOM.render(
	<Main />,
	document.getElementById('root')
);