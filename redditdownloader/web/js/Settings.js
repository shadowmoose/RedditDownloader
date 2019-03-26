class Settings extends React.Component {
	constructor(props) {
		super(props);
		this.state = {settings: {}};
		this.changes = {}
	}

	componentDidMount() {
		eel.api_get_settings()(r=>{
			this.setState({
				settings: r
			});
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
				if('interface.host' in this.changes || 'interface.port' in this.changes){
					alertify
						.alert('Changes to the Web UI will apply the next time you start RMD.')
						.then(()=>{location.reload()})
				}else {
					alertify.closeLogOnClick(true).success("Saved settings! UI will reload in 5 seconds...");
					setTimeout(() => {
						location.reload()
					}, 5000);
				}
			} else{
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
			<SettingsGroup key={group} name={group} list={this.state.settings[group]} change={this.changeSetting.bind(this)}/>
		);

		return (
			<div>
				<p className={'description'}>
					These are the settings RMD uses. Changing them may require a restart to take effect. <br />
					For more information about each setting, go <a href={'https://rmd.page.link/settings'} target={'_blank'}>here</a>.
				</p>
				<button className="fixed bottom right settings_save_btn" onClick={this.saveSettings.bind(this)} disabled={Object.keys(this.changes).length === 0}>
					<i className={'blue icon fa fa-save'}/> Save Settings
				</button>
				<div className="settings_body">
					{settings_groups}
				</div>
			</div>
		);
	}
}



class SettingsGroup extends React.Component {
	constructor(props) {
		super(props);
	}

	titleCase(str) {
		return str.toLowerCase().split(' ').map(function(word) {
			return (word.charAt(0).toUpperCase() + word.slice(1));
		}).join(' ');
	}

	render(){
		let list = this.props.list.map((field) =>
			<SettingsField key={field.name} obj={field} change={this.props.change}/>
		);
		if(list.length === 0){
			return (null); // Render nothing if this group is empty.
		}
		return <form className={"settings_group"}>
			<details open='open'>
				<summary>
					{this.titleCase(this.props.name)}
				</summary>
				{list}
			</details>
		</form>
	}
}


class SettingsField extends React.Component {
	constructor(props) {
		super(props);
		//console.log(this.obj)
	}

	ele_id(){
		let obj = this.props.obj;
		return obj.category + '.' + obj.name; // Build the ID in python's "cat.id" notation. This is used to save properly.
	}

	parse_type(){
		let obj = this.props.obj;
		let ele_id = this.ele_id();
		let change_val = this.props.change;
		if(obj.opts){
			let opts = obj.opts.map((o) =>{
				return <option value={o[0]} title={o[1].toString()} key={o[0]}>{o[0]}</option>
			});
			return <select id={ele_id} defaultValue={obj.value} onChange={change_val} className='settings_input'>
				{opts}
			</select>
		}
		switch(obj.type){
			case 'int':
				return <input type="number" id={ele_id} className='settings_input' defaultValue={obj.value} onChange={change_val}/>;
			case 'bool':
				return <input type="checkbox" id={ele_id} className='settings_input' defaultChecked={obj.value} onChange={change_val}/>;
			default:
				return <input type="text" id={ele_id} className='settings_input' defaultValue={obj.value} onChange={change_val}/>;
		}
	}

	open_oauth(){
		console.log('Opening oauth.');
		eel.api_get_oauth_url()(data => {
			console.log('oAuth data', data);
			let url = data['url'];
			if(!url){
				alertify.closeLogOnClick(true).delay(10000).error(data['message']);
			}else {
				let win = window.open("", '_blank');
				win.location = url;
				win.focus();
				let popupTick = setInterval(function() {
					if (!win || win.closed) {
						clearInterval(popupTick);
						console.log('window closed!');
						alertify.confirm('Reload?', (evt2)=> {
							evt2.preventDefault();
							location.reload(true);
						});
					}
				}, 500);
			}
		})
	}

	render(){
		let obj = this.props.obj;
		if(this.ele_id() === 'auth.refresh_token'){
			return <div className='settings_input_wrapper' title={obj.description.toString()}>
				<a className={"center"} onClick={this.open_oauth.bind(this)}>{obj.value?"Change Authorized Account":"Authorize an account!"}</a>
			</div>
		}
		return <div className='settings_input_wrapper' title={obj.description.toString()}>
			<label htmlFor={this.ele_id()} className='settings_label'>{obj.name.replace(/_/g, ' ')}:</label>
			{this.parse_type()}
		</div>
	}
}
