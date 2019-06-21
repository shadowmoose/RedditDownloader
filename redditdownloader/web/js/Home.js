class Home extends React.Component {
	constructor(props){
		super(props);
		this.state = {version: '', progress: null};
	}

	componentDidMount(){
		eel.api_current_status()(r=>{
			this.setState({version: r['current_version']}, ()=> {
				let last = localStorage.getItem('last-update-check'); // TODO: Wrap localStorage.
				if(last){
					last = JSON.parse(last);
					if(new Date().getTime() - last < 1000*60*60){
						console.debug("Skipping update check until:", new Date(last+1000*60*60).toLocaleString());
						return;
					}
				}
				localStorage.setItem('last-update-check', JSON.stringify(new Date().getTime()));
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
		let tag = data[0].tag_name;
		console.log('Current version:', this.state.version, 'Latest Release:', tag);
		if(tag !== this.state.version) {
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
			let progress = this.state.progress;
			let loading = progress.loader.scanning;
			let dedupe_status = (progress.deduplication.running? progress.deduplication.status: "Off");
			let threads = progress.downloaders.map((thread, idx)=>{
				return <details className={'progressThread '+ (thread.running? 'active':'inactive')} key={idx} open='open'>
					<summary className={thread.running? 'green':'orange'}>Downloader {idx+1}</summary>
					<div className='description'>
						<div><b>File: </b>{thread.file_name}</div>
						<div><b>Handler: </b>{thread.handler}</div>
						<div><b>Status: </b>{thread.status}</div>
						{thread.percent ?<div><b>Percent Done: </b>{thread.percent}%</div> : <div/>}
					</div>
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
					<b>Files Found: </b>{progress.loader.total_found + (loading?' (so far)':'')}
				</div>
				<div className={'blue'}>
					<b>Files Completed: </b>{progress.loader.total_found - progress.loader.queue_size}
				</div>
				<div className={'orange'}>
					<b>In Queue: </b>{progress.loader.queue_size}
				</div>
				<div className={progress.deduplication? 'yellow':'red'}>
					<b>Deduplication: </b> {dedupe_status}
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
					Hover over any UI field or value to see a helpful description. <br /><br />
					If you haven't yet, go to the Settings tab and authorize an account. <br />
					RMD needs this in order to access Reddit! <i className="left_pad red icon fa fa-heart"/>
				</p>
				{progress_display}
			</div>
		);
	}
}
