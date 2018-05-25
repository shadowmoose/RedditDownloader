class Sources extends React.Component {
	constructor(props){
		super(props);
		this.state = {available:[], active:[]}
	}

	componentDidMount() {
		async function run() {
			// Inside a function marked 'async' we can use the 'await' keyword.
			let n = await eel.api_get_sources()(); // Must prefix call with 'await'
			console.log('Got this from Python: ');
			console.log(n);
			return n
		}
		run().then((r)=>{
			this.setState({
				available: r['available'],
				active: r['active']
			});
			console.log('Sources state:');
			console.log(this.state)
		})
	}


	render() {
		let sources = this.state.available.map((s) => //TODO: Switch to "active"
			<Source obj={s} key={s.alias}/>
		);
		return (
			<div>
				<h2>Sources:</h2>
				{sources}
			</div>
		);
	}
}


class Source extends React.Component {
	constructor(props) {
		super(props);
		this.state = props.obj;
		this._save = this.saveSettings.bind(this);
		this._change = this.changeSetting.bind(this);
	}

	saveSettings(){

	}

	getObj(){
		return {
			alias: this.state.alias,
			type: this.state.type,
			data: Object.assign({}, this.state.data),
		};
	}

	changeSetting(evt){
		let targ = evt.target.id.replace('null.','');
		let type = evt.target.type;
		let val = evt.target.value;
		switch(type) {
			case 'checkbox':
				val = evt.target.checked;
				break;
			case 'number':
				val = parseInt(val);
				break;
		}
		if(targ in this.state){
			let ob = {};
			ob[targ] = val.replace(/ /g, '-').toLowerCase();
			this.setState(ob);
		}else {
			let cd = Object.assign({}, this.state.data);
			cd[targ] = val;
			this.setState({data: cd});
		}
	}

	render() {
		console.log('Redrew:', this.state.alias);
		console.log('New Data:', this.state.data);
		console.log('Output Object:', this.getObj());
		let sf = <SourceSettingsGroup name={this.state.alias} type={this.state.type} list={this.state.settings} save={this._save} change={this._change}/>;
		return <div>
			<details open='open'>
				<summary>
					{this.state.alias ? this.state.alias : '[blank]'}
				</summary>
				{sf}
			</details>
		</div>
	}
}

class SourceSettingsGroup extends React.Component {
	constructor(props) {
		super(props);
	}

	render(){
		console.log('redrew group.');
		console.log(this.props);
		let fields = this.props.list.map((field) =>
			<SettingsField key={field.name} obj={field} change={this.props.change}/>
		);
		return <form className={"settings_group"}>
			<div><label>Source Type: </label><span>{this.props.type}</span></div>
			<label htmlFor='alias' title='Rename this Source!'>Name:</label>
			<input type={'text'} id='alias' value={this.props.name} onChange={this.props.change} title='Rename this Source!'/>
			{fields}
		</form>
	}
}