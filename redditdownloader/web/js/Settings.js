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
			return null; // Render nothing if this group is empty.
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
		this.state = {username: null, ...this.state};
	}

	componentDidMount() {
		if(this.ele_id() === 'auth.refresh_token') {
			eel.get_authed_user()(username => {
				console.log('Got authed username:', username);
				this.setState({username})
			})
		}
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
		eel.api_get_oauth_url()(data => {
			let url = data['url'];
			if (!url) {
				alertify.closeLogOnClick(true).delay(10000).error(data['message']);
			} else {
				try {
					win.location = url;
					win.focus();
				} catch(err) {
					alertify.closeLogOnClick(true)
						.delay(10000)
						.error('Cannot open reddit auth url. Manually auth on command line.');
					return
				}

				if (window.location.host !== 'localhost:7505') {
					alertify.prompt('If you are not on localhost, the redirect from Reddit will fail. ' +
						'<br> This is okay. ' +
						'<br> Please enter the url you were redirected to here:', (res) => {
						try {
							const params = new URL(res).searchParams;
							const code = params.get('code');
							const state = params.get('state');
							const loc = `${window.origin}/authorize?state=${state}&code=${code}`;
							try {
								window.open(loc, '_blank')
							} catch(err) {
								console.error(err);
								window.location = loc;
							}
							alertify.confirm(`Reload once you have authorized.<br/>`
								+ `Click <a href="${loc}">here</a> if the auth window did not automatically open.`,
								(evt2) => {
								evt2.preventDefault();
								location.reload();
							});
						} catch (err) {
							console.error(err);
							alertify.closeLogOnClick(true).delay(10000).error('Failed to parse the given URL!');
							location.reload();
						}

					}, () => location.reload );
				} else {
					alertify.confirm('Reload UI now?', (evt2) => {
						evt2.preventDefault();
						location.reload();
					});
				}
			}
		})
	}

	render(){
		let obj = this.props.obj;
		if(this.ele_id() === 'auth.refresh_token') {
			const msg = this.state.username? `Switch Accounts: ${this.state.username}` : 'Change Authorized Account';
			return <div className='settings_input_wrapper' title={obj.description.toString()}>
				<a className={"center"} onClick={this.open_oauth.bind(this)}>{obj.value? msg : "Authorize an account!"}</a>
			</div>
		}
		return <div className='settings_input_wrapper' title={obj.description.toString()}>
			<label htmlFor={this.ele_id()} className='settings_label'>{obj.name.replace(/_/g, ' ')}:</label>
			{this.parse_type()}
		</div>
	}
}
