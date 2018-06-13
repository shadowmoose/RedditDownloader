class Browser extends React.Component {
	constructor(props) {
		super(props);
		this.state = {posts:[]};
		this.search(['title', 'body', 'subreddit'], "aww")
	}

	search(categories, term){
		eel.api_search_posts(categories, term)(n => {
			console.log("Searched posts:", n);
			let posts = [];
			n.forEach((p)=>{
				posts.push(p)
			});
			console.log('posts:', posts);
			this.setState({posts: posts});
		});
	}

	render() {
		let groups = [];
		let i = 0;
		let per_group = Math.ceil(this.state.posts.length / 4);
		let group = [];
		this.state.posts.forEach((p)=>{
			group.push(<MediaContainer post={p} key={i} />);
			i+=1;
			if(i%per_group===0 && i < per_group*4){
				groups.push(<div className="img_column" key={"img_group_"+groups.length}>{group}</div>);
				group = []
			}
		});
		if(group.length>0)
			groups.push(<div className="img_column" key={'img_group_'+groups.length}>{group}</div>);
		return(
			<div>
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
		this.post = props.post;
		this.files = this.post.files;
		this.elements = this.files.map((f)=>{
			return this.parse_media(f);
		}).filter((f)=>{
			return f;
		});
		// TODO: Empty list support (display text block?)
		if(this.elements.length > 1){
			console.log('+Found Media Gallery: ', '('+this.elements.length+')',this.post.title);
		}
		this._next = this.next.bind(this);
		this.state = {index: 0};
	}

	parse_media(file){
		let ext = file[1].split('.').pop();
		switch(ext){
			case 'jpg':
			case 'jpeg':
			case 'png':
			case 'bmp':
			case 'gif':
				return <img src={'/file?id='+file[0]} style={{width:"100%"}} title={this.post.title}/>;
			case 'mp4':
			case "webm":
				return <video width="100%" title={this.post.title} autoPlay controls muted loop>
					<source src={'/file?id='+file[0]} type={"video/"+ext} />
				</video>;
			default:
				console.log('Cannot handle media:', file);
				return <div style={{width:"100%", height:"100px"}} title={this.post.title}>Empty</div>;
		}
	}

	next(){
		console.log('Next image...', this.state.index);
		this.setState({index: (this.state.index+1) % this.elements.length})
	}

	render() {
		let special = [];
		if(this.elements.length > 1)
			special.push(<i className={'media_gallery_icon icon fa fa-list-ul'} key={'gallery'} />);
		return (
			<div className={'media_container'} style={{width:"100%"}} onClick={this._next}>
				{special}
				{this.elements[this.state.index]}
			</div>
		);
	}
}