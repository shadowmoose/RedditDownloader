class Sources extends React.Component {
	constructor(props){
		super(props);
		this.state = {available:[], active:[], filters: {}};
		eel.api_get_sources()(r=>{
			console.log(r);
			this.setState({
				available: r['available'],
				active: r['active'],
				filters: r['filters']
			});
		});
		this._add = this.addSource.bind(this);
		this._update = this.updateSource.bind(this);
		this._save_all = this.saveAll.bind(this);
		this._delete = this.deleteSource.bind(this);
	}

	addSource(evt){
		let type = evt.target.value;
		let base_obj = clone(this.state.available).filter((s)=>{
			return s.type === type
		})[0];
		//console.log('Adding source of type:', type);
		alertify.prompt("Setting up a Source for "+base_obj.description.toLowerCase()+"<br/><br/>Enter a unique name for this Source",
			(val, ev) => {
				ev.preventDefault();
				// The value entered is availble in the val variable.
				let alias = val.trim();
				let sources = clone(this.state.active);
				if(alias === ''){
					alertify.error('The name cannot be blank.');
					return;
				}
				for(let i=0;i<sources.length;i++){
					if(sources[i].alias === alias) {
						alertify.error('That alias has already been used!');
						return;
					}
				}
				console.log('Adding source:', base_obj.type, '->', alias);
				base_obj.alias = alias;
				sources.push(base_obj);
				this.setState({active: sources}, ()=>alertify.success('Added new Source! Now configure it!'));
			}, (ev) => {
				// The click event is in the event variable, so you can use it here.
				ev.preventDefault();
				alertify.error("Not adding source.");
			}
		);
	}

	updateSource(original_alias, obj){
		//console.log('Pushing source update:', original_alias, obj);
		let sources = clone(this.state.active).filter((s)=>{
			//console.log('\t+Screening ', s.alias,':', s.alias !== original_alias);
			return s.alias !== original_alias;
		});
		sources.push(obj);
		console.log('Updated active sources:', sources);
		this.setState({active: sources});
	}

	deleteSource(original_alias){
		alertify.confirm('You are about to delete:<br><b>'+original_alias+' </b><br>Do you want to continue?', function(){
			let sources = clone(this.state.active).filter((s)=>{
				return s.alias !== original_alias;
			});
			console.log('Deleted & Updated active sources:', sources);
			this.setState({active: sources}, ()=>alertify.success('Deleted source "'+original_alias+"'."));
		}.bind(this), function() {
			alertify.error('Did not delete source.')
		});
	}

	saveAll(){
		console.log('Saving all settings...');
		// noinspection JSUnresolvedFunction
		eel.api_save_sources(this.state.active)(n => {
			if(n){
				alertify.closeLogOnClick(true).success("Saved all Sources!")
			}else{
				alertify.closeLogOnClick(true).error("Error saving sources!")
			}
		});
	}

	render() {
		let sources = this.state.active.sort((a,b)=>{
			return (a.alias > b.alias) ? 1 : ((b.alias > a.alias) ? -1 : 0);
		}).map((s) =>
			<Source obj={s} key={s.alias} filterOptions={this.state.filters} update={this._update} delete={this._delete}/>
		);
		let available_sources = this.state.available.map((s)=>{
			return <option key={s.alias} title={s.description} value={s.type}>{s.description}</option>
		});
		available_sources.unshift(<option key={'none'} value={"none"} disabled>Add a new Source</option>);
		return (
			<div className={'source_container'}>
				<p className={'description'}>
					Sources are the places on Reddit that RMD finds Posts. <br />
					For more information, click <a href={"https://rmd.page.link/sources"} target={"_blank"}>here</a>.
				</p>
				<div className={'source_controls'}>
					<select className={'source_add'} value={'none'} onChange={this._add}>{available_sources}</select>
					<button className={'settings_save_btn fixed bottom right'} onClick={this._save_all}>
						<i className={'blue icon fa fa-save'} title={'Save Sources'} onClick={this._save_all}/>
						<label className={''}> Save Sources</label>
					</button>
				</div>
				<div className={'source_list_wrapper'}>
					{sources}
				</div>
			</div>
		);
	}
}


class Source extends React.Component {
	constructor(props) {
		super(props);
		let ob = clone(props.obj);
		ob.settings.forEach((d)=>{ // Load any preexisting values from the "data" dict.
			if(d.name in ob.data){
				d.value = ob.data[d.name]
			}
		});
		this.state = ob;
		this._change = this.changeSetting.bind(this);
		this._changeFilters = this.changeFilters.bind(this);
		this._state = this.sState.bind(this);
	}

	pushUpdate(original_alias=false){
		if(!original_alias)
			original_alias = this.state.alias;
		this.props.update(original_alias, this.state)
	}

	sState(new_state){
		let oa = clone(this.state.alias);
		this.setState(new_state, () => this.pushUpdate(oa))
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
			this._state(ob);
		}else {
			let cd = clone(this.state.data);
			cd[targ] = val;
			this._state({data: cd});
		}
	}

	changeFilters(new_filter_list){
		//console.log('New filter list:', new_filter_list);
		this._state({filters: new_filter_list});
	}

	render() {
		return <div className={'source_full_wrapper'}>
			<details open='open'>
				<summary>
					{this.state.alias ? this.state.alias : '[blank]'}
					<span onClick={(e)=>{e.preventDefault(); this.props.delete(this.state.alias)}} className={'source_delete'} title="Delete this Source.">&#10006;</span>
				</summary>
				<div className='description'>{this.state.description}</div>
				<SourceSettingsGroup name={this.state.alias} type={this.state.type} list={this.state.settings} change={this._change}/>
				<SourceFilterGroup filters={this.state.filters} change={this._changeFilters} filterOptions={this.props.filterOptions}/>
			</details>
		</div>
	}
}

class SourceSettingsGroup extends React.Component {
	constructor(props) {
		super(props);
	}

	render(){
		//console.log('redrew group.');
		//console.log(this.props);
		let fields = this.props.list.map((field) =>
			<SettingsField key={field.name} obj={field} change={this.props.change}/>
		);
		return <form className={"source_settings_group settings_group"}>
			<div><label>Source Type: </label><span>{this.props.type}</span></div>
			{fields}
		</form>
	}
}


class SourceFilterGroup extends React.Component {
	constructor(props) {
		super(props);
		this._update = this.update.bind(this);
		this._add_filter = this.add_current_filter.bind(this);
		this._remove = this.remove_filter.bind(this);
		this.state = {filter: this.make_base_filter()}
	}

	update(evt, prop){
		let val = evt.target.value;
		//console.log('Group is Updating Filter: ', prop, '->', val);
		if(prop === 'field'){
			let flt = false;
			this.props.filterOptions.available.forEach((f)=>{
				if(f.field === val)flt = this.make_base_filter(f); // automatically clones.
			});
			if(flt){
				this.setState({filter: flt});
				//console.log('Swapped selected filter type.')
			}else{
				alertify.error('Error finding matching Filter!');
				console.error('Error finding matching filter.');
			}
		}else{
			let nf = clone(this.state.filter);
			nf[prop] = val;
			this.setState({filter: nf});
		}
	}

	add_current_filter(){
		let filters = clone(this.props.filters);
		let newf = clone(this.state.filter);
		if(!newf.limit){
			alertify.error('You must specify a limit!');
			return;
		}
		filters = filters.filter((f)=>{return !(f.field===newf.field && f.operator === newf.operator)}); // Unique field+key combo.
		filters.push(this.state.filter);
		this.setState({filter: this.make_base_filter()});
		//console.log('Pushing new filters up from group:', filters);
		this.props.change(filters); // pass change up.
	}

	remove_filter(obj){
		let field = obj.field;
		let operator = obj.operator;
		let filters = clone(this.props.filters);
		filters = filters.filter((f)=>{return !(f.field===field && f.operator === operator)}); // Unique field+key combo.
		this.props.change(filters); // pass change up.
	}

	format_operator(op){
		return String(op).replace('.','').replace('match', 'matches')
	}

	make_base_filter(fil=null){
		let f = fil ? clone(fil) : clone(this.props.filterOptions.available[0]);
		if(!f.operator){
			f.operator = this.props.filterOptions.operators[0]
		}
		if(!f.limit){
			f.limit = ''
		}
		return f;
	}

	render(){
		//console.log('Filter Group Rerender:', this.state.filter);
		let filter = this.state.filter;

		let operators = this.props.filterOptions.operators.map((o)=>{
			return <option key={o} value={o}>{this.format_operator(o)}</option>
		});
		let fieldOpts = this.props.filterOptions.available.map((o)=>{
			return <option key={o.field} value={o.field} title={o.description}>{o.field}</option>
		});

		let fieldSelect = <select className='filter_field' onChange={(e) => this._update(e, 'field')} value={filter.field ? filter.field : ''} title={filter.description}>{fieldOpts}</select>;
		let operator = <select className='filter_operator' onChange={(e) => this._update(e, 'operator')} value={filter.operator? filter.operator : ''} disabled={!filter.accepts_operator}>{operators}</select>;
		let limit = <input type='text' className='filter_limit' onChange={(e) => this._update(e, 'limit')} value={filter.limit ? filter.limit : ''}/>;

		let filters = this.props.filters.map((field) =>
			<FilterField key={field.field+field.limit} obj={field} remove={this._remove}/>
		);
		let prompt = this.props.filters.length > 0 ? 'Use Filters:' : 'Filter the Posts from this Source:';
		return <form className={"source_filter_group"}>
			<div><b className={'source_filter_prompt'}>{prompt}</b></div>
			<div className={'source_add_filter_wrapper'}>
				{fieldSelect}
				{operator}
				{limit}
				<i className={'green align_to_text left_pad hover_shadow icon fa fa-plus-square'} onClick={this._add_filter} title={"Add Filter"}/>
			</div>

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

	convert_symbol(sym){
		switch(sym){
			case '.min':
				return '>=';
			case '.max':
				return '<=';
			case '.equals':
				return 'is';
			case '.match':
				return 'matches pattern';
			default:
				return sym;
		}
	}

	render(){
		return <li className="source_filter_wrapper">
			<b className={'filter_field'}>{this.props.obj.field}</b>
			<em className={'filter_operator'}> {this.convert_symbol(this.props.obj.operator)}</em>
			<span className={'filter_limit'}> {this.props.obj.limit}</span>
			<span onClick={(e)=>{e.preventDefault(); this.props.remove(this.props.obj)}} className={'source_delete'} title="Delete this Filter.">&#10006;</span>
		</li>
	}
}
