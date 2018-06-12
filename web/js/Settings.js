class Settings extends React.Component {
	constructor(props) {
		super(props);
		this.state = {settings: {}};
		this.changes = {}
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

	/** Trigger save event for all settings compontents. */
	saveSettings(){
		if(Object.keys(this.changes).length === 0) {
			alertify.closeLogOnClick(true).delay(1000).log("No settings have been changed!");
			return;
		}
		console.log('Saving all settings...');
		eel.api_save_settings(this.changes)(n => {
			if(n){
				alertify.closeLogOnClick(true).success("Saved settings!")
			}else{
				alertify.closeLogOnClick(true).error("Error saving settings!")
			}
			this.changes = {};
			this.setState({changes: {}})
		});
	}

	/** Setting <input> fields bubble their changes up to here. */
	changeSetting(event){
		let type = event.target.type;
		let val = event.target.value;
		switch(type){
			case 'checkbox':
				val = event.target.checked;
				break;
			case 'number':
				val = parseInt(val);
				break;
		}
		console.log('Changed: ', event.target.id, val);
		this.changes[event.target.id] = val;
		this.setState({changes: clone(this.changes)});
	}

	render() {
		const settings_groups = Object.keys(this.state.settings).map((group) =>
			<SettingsGroup key={group} name={group} list={this.state.settings[group]} save={this.saveSettings.bind(this)} change={this.changeSetting.bind(this)}/>
		);

		return (
			<div>
				<p className={'description'}>
					These are the settings RMD uses. Changing them may require a restart to take effect. <br />
					For more information about each setting, go <a href={'https://github.com/shadowmoose/RedditDownloader/blob/master/docs/Settings.md'} target={'_blank'}>here</a>.
				</p>
				<input type="button" className="settings_save_btn" onClick={this.saveSettings.bind(this)} value="Save Settings" disabled={Object.keys(this.changes).length === 0}/>
				<div className="settings_body">
					{settings_groups}
				</div>
				<input type="button" className="settings_save_btn" onClick={this.saveSettings.bind(this)} value="Save Settings" disabled={Object.keys(this.changes).length === 0}/>
			</div>
		);
	}
}



class SettingsGroup extends React.Component {
	constructor(props) {
		super(props);
		this.name = props.name;
		this.list = props.list;
		this.changeSetting = props.change;
		let fields = this.list.map((field) =>
			<SettingsField key={field.name} obj={field} change={this.changeSetting}/>
		);
		this.state = {elems: fields}
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
			<details open='open'>
				<summary>
					{this.titleCase(this.name)}
				</summary>
				{this.state.elems}
			</details>
		</form>
	}
}


class SettingsField extends React.Component {
	constructor(props) {
		super(props);
		this.obj = props.obj;
		this.state = {value: this.obj.value};
		this.type = this.parse_type();
		this.ele_id = this.obj.category + '.' + this.obj.name; // Build the ID in python's "cat.id" notation. This is used to save properly.
		this.changeVal = props.change;
		//console.log(this.obj)
	}

	parse_type(){
		if(this.obj.opts){
			let opts = this.obj.opts.map((o) =>{
				return <option value={o[0]} title={o[1].toString()} key={o[0]}>{o[0]}</option>
			});
			return <select id={this.ele_id} defaultValue={this.state.value} onChange={this.changeVal} className='settings_input'>
				{opts}
			</select>
		}
		switch(this.obj.type){
			case 'int':
				return <input type="number" id={this.ele_id} className='settings_input' defaultValue={this.state.value} onChange={this.changeVal}/>;
			case 'bool':
				return <input type="checkbox" id={this.ele_id} className='settings_input' defaultChecked={this.state.value} onChange={this.changeVal}/>;
			default:
				return <input type="text" id={this.ele_id} className='settings_input' defaultValue={this.state.value} onChange={this.changeVal}/>;
		}
	}

	render(){
		return <div className='settings_input_wrapper' title={this.obj.description.toString()}>
			<label htmlFor={this.ele_id} className='settings_label'>{this.obj.name.replace(/_/g, ' ')}:</label>
			{this.parse_type()}
		</div>
	}
}