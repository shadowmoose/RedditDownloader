class Settings extends React.Component {
	constructor(props) {
		super(props);
		this.state = {settings: {}};
	}

	componentDidMount() {
		async function run() {
			// Inside a function marked 'async' we can use the 'await' keyword.
			let n = await eel.api_get_settings()(); // Must prefix call with 'await'
			console.log('Got this from Python: ');
			console.log(n);
			return n
		}
		run().then((r)=>{
			this.setState({
				settings: r
			});
			console.log('Settings state:');
			console.log(this.state)
		})
	}

	componentWillUnmount() {

	}

	render() {
		const settings_groups = Object.keys(this.state.settings).map((group) =>
			<SettingsGroup key={group} name={group} obj={this.state.settings[group]} />
		);

		return (
			<div>
				<div className="settings_body">
					{settings_groups}
				</div>
				<button>Save</button>
			</div>
		);
	}
}



class SettingsGroup extends React.Component {
	constructor(props) {
		super(props);
		this.name = props.name;
		this.list = props.obj;
		this.fields = this.list.map((field) =>
			<SettingsField key={field.name} obj={field} />
		);
		console.log('Props:', this.list)
	}

	titleCase(str) {
		return str.toLowerCase().split(' ').map(function(word) {
			return (word.charAt(0).toUpperCase() + word.slice(1));
		}).join(' ');
	}

	render(){
		if(this.list.length === 0){
			return (null); // Render nothing if this group is empty.
		}
		return <form className={"settings_group"}>
			<h2 className="settings_group_title">{this.titleCase(this.name)}</h2>
			{this.fields}
		</form>
	}
}


class SettingsField extends React.Component {
	constructor(props) {
		super(props);
		this.obj = props.obj;
		this.type = this.parse_type();
		console.log(this.obj)
	}

	parse_type(){
		switch(this.obj.type){
			case 'int':
				return <input type="number" id={this.obj.name} className='settings_input' defaultValue={this.obj.value} />;
			case 'bool':
				return <input type="checkbox" id={this.obj.name} className='settings_input' defaultChecked={this.obj.value}/>;
			default:
				return <input type="text" id={this.obj.name} className='settings_input' defaultValue={this.obj.value}/>;
		}
	}

	render(){
		return <div className='settings_input_wrapper' title={this.obj.description}>
			<label htmlFor={this.obj.name} className='settings_label'>{this.obj.name.replace(/_/g, ' ')}:</label>
			{this.parse_type()}
		</div>
	}
}