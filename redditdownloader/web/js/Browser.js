class Browser extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			posts:[],
			total: 0,
			term:'',
			fields:[],
			autoplay: window.lRead('browser-autoplay', true),
			page_size: 25,
			page: 0
		};
		this.search_timer = null;
		this._toggle_field = this.toggle_field.bind(this);
		this._search_term = this.change_search_term.bind(this);
		this._autoplay = this.autoplay.bind(this);
		this._set_page = this.setPage.bind(this);
	}

	componentDidMount(){
		eel.api_searchable_fields()(n => {
			let fields = {};
			n.forEach((p)=>{
				fields[p] = true
			});
			this.setState({fields: fields});
		});
		this.schedule_search();
	}

	search(page=0){
		console.log('Running search, Page:', page);
		let fields = Object.keys(this.state.fields).filter((f)=> {
			return this.state.fields[f];
		});
		let term = this.state.term;
		console.log("Searching:", fields, term);
		eel.api_search_posts(fields, term, this.state.page_size, page)(n => {
			console.log("Searched posts:", n);
			let posts = n.results;
			this.setState({posts, page, total: n.total});
			console.debug('New Browser State:', this.state);
		});
	}

	schedule_search(delay=250){
		if(this.search_timer !== false)
			clearTimeout(this.search_timer);
		this.search_timer = setTimeout(() => {this.search(0)}, delay);
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
		window.lStore('browser-autoplay', event.target.checked);
		this.setState({autoplay: event.target.checked});
	}

	setPage(evt, idx){
		evt.preventDefault();
		this.setState({page: idx}, ()=>{this.search(this.state.page)});
	}

	chunkify(a, n, balanced) {// Split array [a] into [n] arrays of roughly-equal length.
		if (n < 2)
			return [a];
		if (!a)
			return [];
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

	render() {
		let groups = [];
		let group = [];
		let chunks = this.chunkify(this.state.posts, 4, true);
		chunks.forEach((ch)=>{
			ch.forEach((p)=>{
				group.push(<MediaContainer post={p} key={p.reddit_id} autoplay={this.state.autoplay}/>);
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
		let pages = Math.ceil(this.state.total / this.state.page_size);
		if(start<0)end+=Math.abs(0-start);
		if(end>=pages)start-=(end - pages);
		start = Math.max(0, start);
		end = Math.min(pages, end);
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
					<div className={'pagination '+(this.state.total>0?'':'hidden')}>
						<a onClick={(e)=>(this._set_page(e, 0))}>&laquo;</a>
						{page_buttons}
						<a onClick={(e)=>(this._set_page(e, pages-1))}>&raquo;</a>
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
		this.is_video = false;
		this._next = this.next.bind(this);
		this._close = this.close.bind(this);
		this._mute_toggle = this.mute_toggle.bind(this);
		this._handle_key = this.handleKey.bind(this);
	}

	static getDerivedStateFromProps(props) {
		return {
			post: props.post,
			files: props.post.files,
			autoplay: props.autoplay
		};
	}

	handleKey(e){
		if(!this.state.lightbox) return;
		// right
		if (e.keyCode === 39) {
			this._next(e, 1)
		}
		// left
		if (e.keyCode === 37) {
			this._next(e, -1)
		}
	}

	componentDidMount() {
		window.addEventListener('keydown', this._handle_key)
	}

	componentWillUnmount() {
		window.removeEventListener('keydown', this._handle_key)
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
				return <img src={'/file?id='+file.token} style={{width:"100%"}} className={'media'} alt={this.state.post.title}/>;
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
					controls={this.state.lightbox && !is_small_player}
					preload={'metadata'}
					muted={is_small_player?true: this.state.muted}
					loop>
					<source src={'/file?id='+file.token} type={"video/"+ext} />
				</video>;
			default:
				console.log('Cannot handle media:', file.path);
				return <div style={{width:"100%", height:"100px"}} className={'media center invalid_media'}>Not Media</div>;
		}
	}

	next(event, step=1){
		event.stopPropagation();
		let nidx = this.state.index;
		if(this.state.lightbox) {
			let clickTarget = event.target;
			while(!clickTarget.classList.contains('lightbox') && clickTarget.parentElement) {
				// Elevate target to the Lightbox parent.
				clickTarget = clickTarget.parentElement;
			}
			const clickTargetWidth = clickTarget.offsetWidth;
			const xCoordInClickTarget = event.clientX - clickTarget.getBoundingClientRect().left;
			if (clickTargetWidth / 2 > xCoordInClickTarget) {
				nidx = (nidx - step);
			} else {
				nidx = (nidx + step) % this.state.files.length;
			}
		}
		if(nidx<0)
			nidx = this.state.files.length - 1;
		console.log('New index:', nidx);
		this.setState({index: nidx, lightbox: true})
	}

	mute_toggle(evt){
		if(evt.target.buffered.length===0){
			console.log('No mute changes while loading.');
			return; // This could probably be made more reliable, if there's a better way to detect unloading.
		}
		this.setState({muted: evt.target.muted})
	}

	close(evt){
		evt.stopPropagation();
		console.log('Closing...');
		this.setState({lightbox: false})
	}

	componentDidUpdate(prevProps, prevState){
		if(this.refs.video) {
			if(!prevState.autoplay && this.state.autoplay)
				this.refs.video.play();
			if(prevState.autoplay && !this.state.autoplay)
				this.refs.video.pause();
		}
	}

	render() {
		let reddit_url = 'http://redd.it/' + (this.state.post.parent_id? this.state.post.parent_id : this.state.post.reddit_id).replace('t3_','');
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
							<i className={'vcenter left icon shadow fa fa-arrow-circle-o-left'} title={'Previous'}/>
							<i className={'vcenter right icon shadow fa fa-arrow-circle-o-right'} title={'Next'}/>
							<span className={'bottom black_bkg'}>{this.state.index+1}/{this.state.files.length}</span>
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
