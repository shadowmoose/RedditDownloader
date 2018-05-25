class Sources extends React.Component {
	constructor(props){
		super(props);
		this.state = {available:[], active:[], filters: {}}
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
				active: r['active'],
				filters: r['filters']
			});
			console.log('Sources state:');
			console.log(this.state)
		})
	}


	render() {
		let sources = this.state.available.map((s) => //TODO: Switch to "active"
			<Source obj={s} key={s.alias} filterOptions={this.state.filters}/>
		);
		return (
			<div>
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
		this._changeFilter = this.changeFilter.bind(this);
	}

	saveSettings(){

	}

	getObj(){
		return {
			alias: this.state.alias,
			type: this.state.type,
			data: Object.assign({}, this.state.data),
		}
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

	changeFilter(obj){
	}

	render() {
		console.log('Redrew:', this.state.alias);
		console.log('New Data:', this.state.data);
		console.log('Output Object:', this.getObj());
		return <div>
			<details open='open'>
				<summary>
					{this.state.alias ? this.state.alias : '[blank]'}
				</summary>
				<div className='description'>{this.state.description}</div>
				<SourceSettingsGroup name={this.state.alias} type={this.state.type} list={this.state.settings} save={this._save} change={this._change}/>
				<SourceFilterGroup filters={this.state.filters} change={this._changeFilter} filterOptions={this.props.filterOptions}/>
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


class SourceFilterGroup extends React.Component {
	constructor(props) {
		super(props);
		this._update = this.update.bind(this);
		this.state = {filter: props.filterOptions.available[0]}
	}

	update(evt, prop){
		let val = evt.target.value;
		console.log('Group is Updating Filter: ', prop, '->', val);
		if(prop === 'field'){
			let flt = false;
			this.props.filterOptions.available.forEach((f)=>{
				if(f.field === val)flt = JSON.parse(JSON.stringify(f));
			});
			if(flt){
				this.setState({filter: flt});
				console.log('Swapped filters.')
			}else{
				alertify.error('Error finding matching Filter!');
				console.error('Error finding matching filter.');
			}
		}else{
			let nf = JSON.parse(JSON.stringify(this.state.filter));
			nf[prop] = val;
			this.setState({filter: nf});
		}
	}

	format_operator(op){
		return String(op).replace('.','').replace('match', 'matches')
	}

	render(){
		console.log('Filter Group Rerender:', this.state.filter);
		let filter = this.state.filter;

		let opts = this.props.filterOptions.operators.map((o)=>{
			return <option key={o} value={o}>{this.format_operator(o)}</option>
		});
		let operator = <select className='filter_operator' onChange={(e) => this._update(e, 'operator')} defaultValue={filter.operator} disabled={!filter.accepts_operator}>{opts}</select>;


		let fieldOpts = this.props.filterOptions.available.map((o)=>{
			return <option key={o.field} value={o.field} title={o.description}>{o.field}</option>
		});
		let fieldSelect = <select className='filter_field' onChange={(e) => this._update(e, 'field')} defaultValue={filter.field} title={filter.description}>{fieldOpts}</select>;


		let limit = <input type='text' className='filter_limit' onChange={(e) => this._update(e, 'limit')} value={filter.limit ? filter.limit : ''}/>;

		let filters = this.props.filterOptions.available.map((field) => //TODO: Should be props.filters.
			<FilterField key={field.field+field.limit} obj={field}/>
		);

		return <form className={"source_filter_group"}>
			<div><b>Filter Group:</b></div>
			{fieldSelect}
			{operator}
			{limit}
			<button>Add Filter</button>
			<ul className="source_filter_list">
				{filters}
			</ul>
		</form>
	}
}


class FilterField extends React.Component {
	constructor(props) {
		super(props);
	}

	render(){
		return <li className="source_filter_field">
			{JSON.stringify(this.props.obj)}
		</li>
	}
}