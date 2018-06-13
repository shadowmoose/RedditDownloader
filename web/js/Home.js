class Home extends React.Component {
	constructor(props){
		super(props);
		this.state = {version: ''};

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
		})
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

	render() {
		return (
			<div>
				<h2>Welcome to the RMD {this.state.version} WebUI!</h2>
				<p>
					It's still in super-early Alpha right now, but I appreciate the testing!<i className="fa fa-heart"/>
				</p>
				<p>
					It still needs a ton of styling, but if you're confused about a setting,
					hovering over it will give you more information.
				</p>
				<p>
					Head over to the other two tabs above, and use them to configure everything!
				</p>
				<p>
					<strong>Keep in mind - </strong>
					settings related to the UI will require you to restart before they take effect!
				</p>
			</div>
		);
	}
}