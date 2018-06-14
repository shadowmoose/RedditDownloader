class Browser extends React.Component {
	constructor(props) {
		super(props);
		this.state = {posts:[[]], term:'', fields:[], autoplay: true, page_size: 50, page: 0};
		this.search_timer = null;
		eel.api_searchable_fields()(n => {
			let fields = {};
			n.forEach((p)=>{
				fields[p] = true
			});
			this.setState({fields: fields});
		});
		this._toggle_field = this.toggle_field.bind(this);
		this._search_term = this.change_search_term.bind(this);
		this._autoplay = this.autoplay.bind(this);
		this._set_page = this.setPage.bind(this);
	}

	search(){
		console.log('Running search');
		let fields = Object.keys(this.state.fields).filter((f)=> {
			return this.state.fields[f];
		});
		let term = this.state.term;
		if(term.trim() === '')
			return;
		console.log("Searching:", fields, term);
		eel.api_search_posts(fields, term)(n => {
			console.log("Searched posts:", n);
			let posts = this.paginate(n, this.state.page_size);
			console.log('posts:', posts);
			this.setState({posts: posts, page: 0});
		});
	}

	schedule_search(){
		if(this.search_timer !== false)
			clearTimeout(this.search_timer);
		this.search_timer = setTimeout(this.search.bind(this), 250);
	}

	toggle_field(event){
		let id = event.target.id;
		let val = event.target.checked;
		let fields = clone(this.state.fields);
		fields[id] = val;
		this.setState({fields: fields}, ()=>{this.schedule_search()});
	}

	change_search_term(event){
		let val = event.target.value;
		if(this.search_timer !== false)
			clearTimeout(this.search_timer);
		this.setState({term: val}, ()=>{this.schedule_search()});
	}

	autoplay(event){
		this.setState({autoplay: event.target.checked});
	}

	setPage(evt, idx){
		evt.preventDefault();
		this.setState({page: idx});
	}

	chunkify(a, n, balanced) {// Split array [a] into [n] arrays of roughly-equal length.
		if (n < 2)
			return [a];
		let len = a.length,
			out = [],
			i = 0,
			size;
		if (len % n === 0) {
			size = Math.floor(len / n);
			while (i < len) {
				out.push(a.slice(i, i += size));
			}
		}else if (balanced) {
			while (i < len) {
				size = Math.ceil((len - i) / n--);
				out.push(a.slice(i, i += size));
			}
		}else {
			n--;
			size = Math.floor(len / n);
			if (len % size === 0)
				size--;
			while (i < size * n) {
				out.push(a.slice(i, i += size));
			}
			out.push(a.slice(size * n));
		}
		return out;
	}

	paginate(arr, size=10){
		// Split the given array into smaller arrays limited by [size]
		let arrs = [];
		while(arr.length) {
			arrs.push(arr.splice(0,size));
		}
		return arrs;
	}

	render() {
		let groups = [];
		let group = [];
		let chunks = this.chunkify(this.state.posts[this.state.page], 4, true);
		chunks.forEach((ch)=>{
			ch.forEach((p)=>{
				group.push(<MediaContainer post={p} key={p.id} autoplay={this.state.autoplay}/>);
			});
			groups.push(<div className="img_column" key={"img_group_"+groups.length}>{group}</div>);
			group = [];
		});

		let categories = Object.keys(this.state.fields).map((f)=>{
			return <div key={f} className={'search_field_group'} title={'Search within '+f}>
				<label htmlFor={f} >{f}</label>
				<input id={f} type={'checkbox'} defaultChecked={this.state.fields[f]} onChange={this._toggle_field}/>
			</div>
		});

		let page_buttons = [];
		let idx = this.state.page;
		let start = idx-2;
		let end = idx+3;
		if(start<0)end+=Math.abs(0-start);
		if(end>=this.state.posts.length)start-=(end - this.state.posts.length);
		start = Math.max(0, start);
		end = Math.min(this.state.posts.length, end);
		for(let i=start; i<end; i++){
			page_buttons.push(
				<a
				onClick={(e)=>(this._set_page(e, i))}
				key={'page_select_'+i}
				className={i===this.state.page?'pagination_active':''}>{i+1}</a>
			);
		}

		return(
			<div>
				<div className={'center'}>
					<label className={'search_field_group'} htmlFor={'search_term'}>Search for downloaded media:</label>
					<input type={'text'} id={'search_term'} className={'settings_input'} value={this.state.term} onChange={this._search_term}/>
					<label htmlFor="autoplay" title={'Autoplay videos?'}><i className={'align_to_text left_pad icon hover_shadow fa fa-play-circle '+(this.state.autoplay?'green':'red')}/></label>
					<input id='autoplay' type={'checkbox'} defaultChecked={this.state.autoplay} onChange={this._autoplay} className={'hidden'}/>
					<div className={'search_group'}>
						<div className={'search_categories'}> {categories}</div>
					</div>
				</div>
				<div className={'center'}>
					<div className={'pagination '+(this.state.posts[0].length>0?'':'hidden')}>
						<a onClick={(e)=>(this._set_page(e, 0))}>&laquo;</a>
						{page_buttons}
						<a onClick={(e)=>(this._set_page(e, this.state.posts.length-1))}>&raquo;</a>
					</div>
				</div>
				<div className="img_row">
					{groups}
				</div>
			</div>
		);
	}
}



class MediaContainer extends React.Component {
	constructor(props) {
		super(props);
		this.state = {index:0, lightbox:false, post: props.post, files: props.post.files, autoplay: props.autoplay, muted: true};
		// TODO: Empty list support (display text block?)
		this.is_video = false;
		this._next = this.next.bind(this);
		this._close = this.close.bind(this);
		this._mute_toggle = this.mute_toggle.bind(this);
	}

	static getDerivedStateFromProps(props, state) {
		return {
			post: props.post,
			files: props.post.files,
			autoplay: props.autoplay
		};
	}

	parse_media(file, is_small_player=false){
		let ext = file.path.split('.').pop();
		this.is_video = false;
		switch(ext){
			case 'jpg':
			case 'jpeg':
			case 'png':
			case 'bmp':
			case 'gif':
			case 'ico':
				return <img src={'/file?id='+file.token} style={{width:"100%"}} className={'media'}/>;
			case 'mp4':
			case "webm":
				this.is_video = true;
				return <video
					width="100%"
					key={'vid_'+file.path+is_small_player}
					className={'media'}
					ref={is_small_player?'video':null} // only mount the video control callback for the preview embed.
					onVolumeChange={this._mute_toggle}
					autoPlay={this.state.autoplay || this.state.lightbox && !is_small_player}
					controls={this.state.autoplay || this.state.lightbox && !is_small_player}
					preload={'metadata'}
					muted={is_small_player?true: this.state.muted} //TODO: Maybe just implement local cookie storage.
					loop>
					<source src={'/file?id='+file.token} type={"video/"+ext} />
				</video>;
			default:
				console.log('Cannot handle media:', file.path);
				return <div style={{width:"100%", height:"100px"}} className={'media center invalid_media'}>Invalid Media</div>;
		}
	}

	next(event, step=1){
		event.stopPropagation();
		let nidx = this.state.index;
		if(this.state.lightbox) {
			nidx = (nidx + step) % this.state.files.length;
		}
		console.log('New index:', nidx);
		if(nidx<0)
			nidx = this.state.files.length - 1;
		this.setState({index: nidx, lightbox: true})
	}

	mute_toggle(evt){
		if(evt.target.buffered.length===0){
			console.log('No mute changes while loading.');
			return; //TODO: This could probably be made more reliable, if there's a better way to detect unloading.
		}
		this.setState({muted: evt.target.muted})
	}

	close(evt){
		evt.stopPropagation();
		console.log('Closing...');
		this.setState({lightbox: false})
	}

	componentDidUpdate(prevProps, prevState, snapshot){
		if(this.refs.video) {
			if(!prevState.autoplay && this.state.autoplay)
				this.refs.video.play();
			if(prevState.autoplay && !this.state.autoplay)
				this.refs.video.pause();
		}
	}

	render() {
		let reddit_url = 'http://redd.it/' + (this.state.post.parent? this.state.post.parent : this.state.post.id).replace('t3_','');
		let special = []; // Special elements to overlay on this box.
		let media = this.parse_media(this.state.files[this.state.index], true);

		if(this.state.files.length > 1)
			special.push(<i className={'media_gallery_icon icon shadow fa fa-list-ul'} key={'gallery'} />);
		if(this.is_video && !this.state.autoplay)
			special.push(<i className={'bottom right icon shadow fa fa-video-camera'} key={'video'} />);
		if(this.state.lightbox){
			special.push(<div key={'lightbox'}>
				<div className={'lightbox_fade'} onClick={this._close} />
				<div className={'lightbox'}>
					{this.parse_media(this.state.files[this.state.index], false)}
					<div className={'lightbox_overlay top'}>
						<h3>{this.state.post.title}</h3>
						<a href={reddit_url} target={'_blank'} title={'Go to post on Reddit'} className={'no_bot'}>{this.state.post.author} in {this.state.post.subreddit}</a>
					</div>
					{this.state.files.length > 1 &&
						<div className={'lightbox_overlay'}>
							<i className={'vcenter left icon shadow fa fa-arrow-circle-o-left'} onClick={(e)=>{this._next(e, -1)}} title={'Previous'}/>
							<i className={'vcenter right icon shadow fa fa-arrow-circle-o-right'} onClick={(e)=>{this._next(e, 1)}} title={'Next'}/>
						</div>
					}
				</div>
			</div>);
		}

		return (
			<div className={'media_container'} style={{width:"100%"}} onClick={this._next}>
				{special}
				<div title={this.state.post.title}>
					{media}
				</div>
			</div>
		);
	}
}


class LightBox extends React.Component {
	constructor(props) {
		super(props);
		this.media = props.media;
		this.index = props.index;
		this.post = props.post;
		console.log("Lightbox:", this.media[this.index]);
		this._close = this.close.bind(this);
	}

	close(){
		console.log('Closing lightbox.');
	}

	render() {
		return (<div>
			<div className={'lightbox_fade'} onClick={this._close} />
			<div className={'lightbox'}>
				{this.media[this.index]}
			</div>
		</div>);
	}
}