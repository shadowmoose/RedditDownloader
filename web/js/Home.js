class Home extends React.Component {
	constructor(props){
		super(props);
		this.state = {version: '', progress: null};

		async function run() {
			// Inside a function marked 'async' we can use the 'await' keyword.
			let n = await eel.api_current_status()(); // Must prefix call with 'await'
			console.log('RMD State:', n);
			return n
		}
		run().then((r)=>{
			this.setState({version: r['current_version']}, ()=> {
				let xhttp = new XMLHttpRequest();
				let self = this;
				xhttp.onreadystatechange = function () {
					if (this.readyState === 4 && this.status === 200) {
						self.updates_loaded(this.responseText)
					}
				};
				xhttp.open("GET", "https://api.github.com/repos/shadowmoose/RedditDownloader/releases", true);
				xhttp.send();
			})
		});
	}

	updates_loaded(resp){
		let data = JSON.parse(resp);
		let converter = new showdown.Converter();
		let body = data[0].body;
		let tag = parseFloat(data[0].tag_name);
		console.log('Current version:', this.state.version, 'Latest Release:', tag);
		if(tag <= parseFloat(this.state.version)) {
			return;
		}
		body  = body.replace(/</g, '&lt').replace(/>/g, '&gt');
		let html = converter.makeHtml(body);
		html = html.replace(/<\s?a\s/g, '<a target="_blank" ');
		alertify
			.delay(8000)
			.log('<div class="clickable_alert">A newer version (RMD '+data[0].tag_name+') is available!<br> Click here to read more!</div>',(evt)=>{
				evt.preventDefault();
				alertify
					.okBtn("Go to page")
					.cancelBtn("Ignore")
					.confirm('<div class="alert_div">'+html+"</div>", (evt2)=>{
						evt2.preventDefault();
						window.open('https://github.com/shadowmoose/RedditDownloader/releases/tag/'+data[0].tag_name);
					});
				alertify.reset();
			});
		alertify.reset();
	}

	set_download_progress(prog){
		// Hook used by App to update all child pages that can accept this data.
		this.setState({progress: clone(prog)});
	}

	render() {
		let progress_display = null;
		if(this.state.progress && 'summary' in this.state.progress){
			let summ = this.state.progress.summary;
			progress_display = <details open={'open'}>
				<summary className={'center'}>
					Download Progress
				</summary>
				<h3 className={'center'}>Complete</h3>
				<div className={'green'}>
					<b>New Posts: </b>{summ.total}
				</div>
				<div className={'blue'}>
					<b>New Files Downloaded: </b>{summ.new_files}
				</div>
				<div className={'red'}>
					<b>Total Failed File Downloads: </b>{summ.failed}
				</div>
				<div className={'orange'}>
					<b>Completed In: </b>{(summ.time)}
				</div>
			</details>
		}else if(this.state.progress && this.state.progress.running){
			console.log(this.state.progress);
			let progress = this.state.progress.progress;
			let loading = this.state.progress.loading;
			let threads = progress.threads.map((thread)=>{
				let lines = thread.lines.map((line, idx)=>{
					return <div key={idx}>{line}</div>
				});
				return <details className={'progressThread '+ (thread.running? 'active':'inactive')} key={thread.thread} open='open'>
					<summary className={thread.running? 'green':'orange'}>{thread.thread}</summary>
					<div className='description'>{lines}</div>
				</details>

			});
			progress_display = <details open={'open'}>
				<summary className={'center'}>
					Download Progress
				</summary>
				<h3 className={'center'}>
					{loading? 'Scanning for Posts & Downloading':'Downloading'}
				</h3>
				<div className={'green'}>
					<b>Posts Found: </b>{progress.found + (loading?' (so far)':'')}
				</div>
				<div className={'blue'}>
					<b>Posts Completed: </b>{progress.found - progress.queue_size}
				</div>
				<div className={'orange'}>
					<b>In Queue: </b>{progress.queue_size}
				</div>
				<details open={'open'}>
					<summary>Running Threads</summary>
					{threads}
				</details>
			</details>
		}

		return (
			<div>
				<h2>Welcome to the RMD {this.state.version} WebUI!</h2>
				<p>
					It's still in early Beta right now, but I appreciate the testing!
					<i className="left_pad red icon fa fa-heart"/>
				</p>
				{progress_display}
			</div>
		);
	}
}
