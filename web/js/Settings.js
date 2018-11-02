class Settings extends React.Component {
	constructor(props) {
		super(props);
		this.state = {settings: {}};
		this.changes = {}
	}

	componentDidMount() {
		async function run() {
			return await eel.api_get_settings()();
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
		alertify.confirm('Save settings? This will automatically restart RMD.', (evt2)=>{
			evt2.preventDefault();
			eel.api_save_settings(this.changes)(n => {
				if(n){
					alertify.closeLogOnClick(true).success("Saved settings!");
					alertify.log('Please wait: RMD will restart for settings to take effect, in 5 seconds...');
					eel.api_restart()();
					if('interface.host' in this.changes || 'interface.port' in this.changes){
						console.log(this.state.settings.interface);
						let host = this.changes['interface.host'] ? this.changes['interface.host']:location.hostname;
						let port = this.changes['interface.port'] ? this.changes['interface.port']: (location.port ? location.port:'');
						setTimeout(() => {
								window.location.href = (window.location.protocol+'//'+host+':'+port+'/index.html'+window.location.hash);
						}, 4500);
					} else {
						setTimeout(() => {
							location.reload()
						}, 4500);
					}
				} else{
					alertify.closeLogOnClick(true).error("Error saving settings!")
				}
				this.changes = {};
				this.setState({changes: {}})
			});
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
		let win = window.open("", '_blank');
		eel.api_get_oauth_url()(url => {
			console.log('oAuth url', url);
			if(!url){
				alertify.closeLogOnClick(true).delay(1000).log("Auth (currently) requires the interface to use port 7505!");
			}else {
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
