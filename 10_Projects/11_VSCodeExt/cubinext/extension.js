const vscode = require('vscode');
const path = require('path');
const { gzip } = require('node-gzip');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
	let panel;
	const config = vscode.workspace.getConfiguration('cubinext');
	const decodeServerIpPort = config.get('decodeServerAddress');
	const errorMsg = "decodeServerAddress [${decodeServerIpPort}] is not a valid [IP:Port] pair"
	if(!decodeServerIpPort.includes(":")) throw new Error(errorMsg)

	const s = decodeServerIpPort.split(":")
	if(!(s.length == 2)) throw new Error(errorMsg)

	const IP = s[0]
	const PORT = parseInt(s[1])

	const openCubinCommand = vscode.commands.registerCommand(
		'cubinext.openCubinFile', async () => {
			const fp = await vscode.window.showOpenDialog({
				canSelectFiles: true,
				canSelectFolders: false,
				canSelectMany: true,
				openLabel: 'Select binary file(s)'
			});
			if(fp && fp.length > 0){
				panel = createWebviewPanel(context, fp, IP, PORT);
				if(!panel.webview){
					vscode.window.showErrorMessage('Something went wrong...');
					return;		
				}
			}
		}
	);

	const openEmptyCubinexCommand = vscode.commands.registerCommand(
		'cubinext.openEmptyCubinext', async () => {
			panel = createWebviewPanel(context, null, IP, PORT);
			if(!panel.webview){
				vscode.window.showErrorMessage('Something went wrong...');
				return;		
			}
		}
	);


	// const sendMsg = vscode.commands.registerCommand('cubinext.msg', async () => {
	// 	if (!panel.webview) {
	// 		vscode.window.showErrorMessage('Flutter UI is not open');
	// 		return;
	// 	}

	// 	panel.webview.postMessage("Hi from vscode 👋");
	// });

	context.subscriptions.push(openCubinCommand, openEmptyCubinexCommand);
}

function intToBytes(int) {
	const buffer = new ArrayBuffer(4);
	const view = new DataView(buffer);
	view.setUint32(0, int, false); // false for big-endian
	return new Uint8Array(buffer);
};

async function readFileBytes(filePath, encoder) {
	try {
	  	const byteArray = await vscode.workspace.fs.readFile(vscode.Uri.file(filePath));
		const x = filePath.split('/');
		const path = x.slice(0,-1).join('/');
		const pathEnc = encoder.encode(path);
		const lPathEnc = intToBytes(pathEnc.length)
		const name = x.slice(-1)[0];
		const nameEnc = encoder.encode(name);
		const lNameEnc = intToBytes(nameEnc.length)
		const bits = await gzip(byteArray);
		const lBits = intToBytes(bits.length)
	  	return  Buffer.concat([lPathEnc, pathEnc, lNameEnc, nameEnc, lBits, bits]); // Returns Uint8Array
	} catch (error) {
	  	vscode.window.showErrorMessage(`Error reading file: ${error}`);
	}
}

function createWebviewPanel(context, fpObjs, ip, port) {
	const webBuildPath = path.join(context.extensionPath, 'cubinext', 'build', 'web');
	const webAssetsPath = path.join(webBuildPath, 'assets');
	const filePathObjs = fpObjs
	const ipPort = ip + ":" + port
	const encoder = new TextEncoder();

	var promises = []
	if(fpObjs !== null){
		for(const key in filePathObjs){
			promises.push(readFileBytes(filePathObjs[key].path, encoder));
		}
	}

	const panel = vscode.window.createWebviewPanel(
		'CubinExt', // Unique identifier for this type of panel
		'Cubinext', // Title displayed in the tab
		vscode.ViewColumn.One, // Editor column to show the panel in
		{
			enableScripts: true,
			retainContextWhenHidden: true,
			localResourceRoots: [
				vscode.Uri.file(webBuildPath),
				vscode.Uri.file(webAssetsPath),
			]
		}
	);

	const toWebviewUri = (relativePath) => {
		const filePath = path.join(webBuildPath, relativePath);
		return panel.webview.asWebviewUri(vscode.Uri.file(filePath)).toString();
	};

	const baseUri = toWebviewUri('./');
	const mainDartJsUri = toWebviewUri("main.dart.js");
	const sqliteUri = toWebviewUri('sqlite3.js');
	const sqlDesUri = toWebviewUri('sql-des.js');

	// Set the HTML content
	panel.webview.html = getWebviewContent(context, {
		mainDartJsUri: mainDartJsUri,
		baseUri: baseUri,
		sqliteUri: sqliteUri,
		sqlDesUri: sqlDesUri
	});

	panel.webview.onDidReceiveMessage(
		async (message) => {
			if (message) {
				if(message === '__GetCubinFilePath__'){
					Promise.allSettled(promises).then(x => {
						const cStrBytes = encoder.encode(ipPort);
						const lCStrBytes = cStrBytes.length;
						const lead = new Uint8Array([50]);
						var msgBytes = [intToBytes(lCStrBytes), cStrBytes, lead];
						x.map(xx => msgBytes.push(xx.value));
						const msg = Buffer.concat(msgBytes);
						// const msg = '__GetCubinFilePath__|' + connectionStr; // + "|" + filePathObjs.map(p => p["path"].length + "|" + p["path"]).join("|")
						panel.webview.postMessage(msg.buffer);
					});
				}
				else if(message.slice("[ERROR]".length) == "[ERROR]"){
					vscode.window.showErrorMessage(message);
				}
				else if(message.slice("[WARNING]".length) == "[WARNING]"){
					vscode.window.showWarningMessage(message);
				}
				else{
					vscode.window.showInformationMessage(message);
				}
		   }
		},
		undefined,
		context.subscriptions
	);

	return panel;
}

function getWebviewContent(context, {
	mainDartJsUri,
	baseUri,
	sqliteUri,
	sqlDesUri
}) {

	const historyApiMock = `
<script>
	(function () {
		var mockState = {};
		var originalPushState = history.pushState;
		var originalReplaceState = history.replaceState;

		history.pushState = function (state, title, url) {
			mockState = { state, title, url };
			console.log('Mock pushState:', url);
		};

		history.replaceState = function (state, title, url) {
			mockState = { state, title, url };
			console.log('Mock replaceState:', url);
		};

		Object.defineProperty(window, 'location', {
			get: function () {
				return {
					href: mockState.url || '${baseUri}',
					pathname: '/',
					search: '',
					hash: ''
				};
			}
		});
	})();	 
</script>`;



	return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Flutter App</title>
			<base href="${baseUri}">
        </head>
        <body>
            <h1>Hello from Webview!</h1>
		</body>
		${historyApiMock}
		<script>
			(function () {
			  	const vscode = acquireVsCodeApi();
				globalThis.vscodePostMessage = vscode.postMessage;
			})();
		</script>
		<script src="${sqliteUri}"></script>
		<script src="${sqlDesUri}"></script>
		<script type="module">
			// Initialize Sqlite js...
			globalThis.sqlite3 = await initSqlite();
		</script>
		<script src="${mainDartJsUri}" type="application/javascript"></script>
        </html>
    `;
}

function deactivate() { }
module.exports = {
	activate,
	deactivate
}