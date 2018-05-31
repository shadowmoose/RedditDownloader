class App extends React.Component {
	constructor(props) {
		super(props);
		let hash = window.location.hash.substr(1);
		let current = 0;
		this.pages = [[<Home />, 'Home'], [<Sources />, 'Sources'], [<Settings />, 'Settings']];
		for(let i=0; i < this.pages.length; i++)
			if(this.pages[i][1].toLowerCase() === hash.toLowerCase())
				current = i;
		this.state = {page: current};
		this.openPage = this.openPage.bind(this);
	}


	openPage(page){
		console.log('Switching tab:', page);
		window.location.hash = this.pages[page][1];
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
			return <div key={idx} className={this.state.page === idx? 'active_page_container':'hidden'} >{p[0]}</div>
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