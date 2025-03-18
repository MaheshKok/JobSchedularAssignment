// WebSocket connection for real-time job updates
class JobSocket {
	constructor() {
		this.socket = null;
		this.connected = false;
		this.callbacks = {
			stats: [],
			jobs: [],
			job_update: [],
		};
	}

	connect() {
		// Create WebSocket connection
		const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
		const wsUrl = `${protocol}//${window.location.host}/ws/jobs/`;

		this.socket = new WebSocket(wsUrl);

		// Connection opened
		this.socket.addEventListener("open", (event) => {
			console.log("Connected to job updates");
			this.connected = true;
		});

		// Listen for messages
		this.socket.addEventListener("message", (event) => {
			const data = JSON.parse(event.data);

			// Trigger appropriate callbacks based on message type
			if (data.type && this.callbacks[data.type]) {
				this.callbacks[data.type].forEach((callback) => callback(data.data));
			}
		});

		// Connection closed
		this.socket.addEventListener("close", (event) => {
			console.log("Disconnected from job updates");
			this.connected = false;

			// Try to reconnect after 3 seconds
			setTimeout(() => this.connect(), 3000);
		});

		// Connection error
		this.socket.addEventListener("error", (event) => {
			console.error("WebSocket error:", event);
			this.connected = false;
		});
	}

	// Register callback for specific message type
	on(type, callback) {
		if (this.callbacks[type]) {
			this.callbacks[type].push(callback);
		}
		return this;
	}

	// Request updated job stats
	getStats() {
		if (!this.connected) return;

		this.socket.send(
			JSON.stringify({
				command: "get_stats",
			})
		);
	}

	// Request updated job list
	getJobs(status = null) {
		if (!this.connected) return;

		this.socket.send(
			JSON.stringify({
				command: "get_jobs",
				status: status,
			})
		);
	}

	// Disconnect the socket
	disconnect() {
		if (this.socket) {
			this.socket.close();
		}
	}
}

// Create a singleton instance
const jobSocket = new JobSocket();

// Auto-connect when the script loads
document.addEventListener("DOMContentLoaded", () => {
	jobSocket.connect();
});
