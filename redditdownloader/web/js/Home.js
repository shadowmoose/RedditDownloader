class Home extends React.Component {
	constructor(props){
		super(props);
		this.state = {version: '', progress: null, failed: null};
		this._openFailed = this.open_failed_urls.bind(this);
	}

	componentDidMount(){
		eel.api_current_status()(r=>{
			this.setState({version: r['current_version']}, ()=> {
				let last = window.lRead('last-update-check');
				if(last){
					last = JSON.parse(last);
					if(new Date().getTime() - last < 1000*60*60){
						console.debug("Skipping update check until:", new Date(last+1000*60*60).toLocaleString());
						return;
					}
				}
				window.lStore('last-update-check',new Date().getTime());
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

	open_failed_urls(){
		eel.get_failed()(res => {
			console.debug('Failed Files:', res);
			res.sort((a, b) => (a.subreddit > b.subreddit) ? 1 : -1);
			this.setState({failed: res})
		})
	}

	set_download_progress(prog){
		// Hook used by App to update all child pages that can accept this data.
		this.setState({progress: clone(prog)});
	}

	render() {
		let progress_display = null;
		let failed_display = null;
		if(this.state.progress && 'summary' in this.state.progress){
			let summ = this.state.progress.summary;
			progress_display = <details open={'open'}>
				<summary className={'center'}>
					Total Summary:
				</summary>
				<div className={'green'}>
					<b>Total Submissions: </b>{summ.total_submissions}
				</div>
				<div className={'yellow'}>
					<b>Total Comments: </b>{summ.total_comments}
				</div>
				<div className={'blue'}>
					<b>Files Downloaded: </b>{summ.total_files_dl}
				</div>
				<div className={[summ.total_urls_failed > 0 ? 'red': 'orange', 'clickable', 'hover_shadow'].join(' ')} onClick={this._openFailed}>
					<b>Failed URLs: </b>{summ.total_urls_failed} ({summ.total_urls} total)
				</div>
			</details>
		}else if(this.state.progress && this.state.progress.running){
			console.log(this.state.progress);
			let progress = this.state.progress;
			let loading = progress.loader.scanning;
			let currentSource = progress.loader.current_source;
			let dedupe_status = (progress.deduplication.running? progress.deduplication.status: "Off");
			let threads = progress.downloaders.map((thread, idx)=>{
				let color = thread.running? 'green':'orange';
				if (thread.error) {
					color = 'red';
				}
				return <details className={'progressThread '+ (thread.running? 'active':'inactive')} key={idx} open='open'>
					<summary className={color}>Downloader {idx+1}</summary>
					<div className='description'>
						<div><b>File: </b>{thread.file_name}</div>
						<div><b>Handler: </b>{thread.handler}</div>
						<div><b>Status: </b>{thread.error || thread.status}</div>
						{thread.percent ?<div><b>Percent Done: </b>{thread.percent}%</div> : <div/>}
					</div>
				</details>
			});
			if (progress.deduplication.error) {
				dedupe_status = `Disabled by Error: {${progress.deduplication.error}}`
			}
			progress_display = <details open={'open'}>
				<summary className={'center'}>
					Download Progress
				</summary>
				<h3 className={'center'}>
					{loading? 'Scanning for Posts & Downloading':'Downloading'}
				</h3>
				<div className={'green'}>
					<b>Files Found: </b>{progress.loader.total_found + (loading?` (so far, from "${currentSource}")`:'')}
				</div>
				<div className={'blue'}>
					<b>Files Completed: </b>{progress.loader.total_found - progress.loader.queue_size}
				</div>
				<div className={'orange'}>
					<b>In Queue: </b>{progress.loader.queue_size}
				</div>
				<div className={(progress.deduplication.running && !progress.deduplication.error)? 'yellow':'red'}>
					<b>Deduplication: </b> {dedupe_status}
				</div>
				<details open={'open'}>
					<summary>Running Threads</summary>
					{threads}
				</details>
			</details>
		}

		if(this.state.failed){
			let fails = this.state.failed.map(f => {
				let totalFail = f.urls.every((u)=>u.failed);
				let reddit_url = (
					f.type === 'Comment' ?
						`https://www.reddit.com/r/${f.subreddit}/comments/${f.parent_id}/_/${f.reddit_id}/`:
						'http://redd.it/'+ f.reddit_id
				).replace('/t3_','/').replace('/t1_', '/');
				let urls = f.urls.map(u => {
					if(u.album_id && !u.album_isparent) return null;
					let normURL = u.address.startsWith('/')? 'https://reddit.com'+u.address : u.address;
					let prettyUrl = u.address.length < 50 ? u.address : u.address.substring(0, 47)+'...';
					prettyUrl = prettyUrl.replace('https://', '').replace('http://', '');

					return <tr key={'url-'+u.id}>
						<td>
							<a className={u.processed?(u.failed? 'red':'green'):'orange'} href={normURL} target={'_blank'}>
								{prettyUrl}
							</a>
						</td>
						<td className={'description center'}>
							{u.failure_reason}
						</td>
						<td>
							{u.last_handler}
						</td>
					</tr>
				});
				return <details key={'fail-post-'+f.reddit_id} style={{marginBottom: '20px'}}>
					<summary className={'small_font'}>
						<span className={totalFail?'red':'orange'} style={{marginRight: '5px'}}>{f.subreddit} </span>
						{f.title.length<100? f.title : f.title.substring(0, 97)+'...'}
					</summary>
					<a href={reddit_url} target={'_blank'}>Go to {f.type}</a>
					<table>
						<tbody>
							<tr key={'failed-headers'}>
								<th>URL</th>
								<th>Failure Reason</th>
								<th>Handler</th>
							</tr>
							{urls}
						</tbody>
					</table>
				</details>
			});
			failed_display = <details open={'open'} style={{marginTop: '20px'}}>
				<summary className={'center'}>
					Failed Downloads
				</summary>
				{fails}
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
				{failed_display}
			</div>
		);
	}
}
