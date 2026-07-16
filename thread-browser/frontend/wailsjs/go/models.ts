export namespace main {
	
	export class Message {
	    role: string;
	    content: string;
	    toolName: string;
	    toolCalls: string;
	    timestamp: number;
	
	    static createFrom(source: any = {}) {
	        return new Message(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.role = source["role"];
	        this.content = source["content"];
	        this.toolName = source["toolName"];
	        this.toolCalls = source["toolCalls"];
	        this.timestamp = source["timestamp"];
	    }
	}
	export class ThreadResult {
	    id: string;
	    title: string;
	    startedAt: number;
	    source: string;
	    score: number;
	    snippet: string;
	    matches: string[];
	    filePath: string;
	    webUrl: string;
	
	    static createFrom(source: any = {}) {
	        return new ThreadResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.id = source["id"];
	        this.title = source["title"];
	        this.startedAt = source["startedAt"];
	        this.source = source["source"];
	        this.score = source["score"];
	        this.snippet = source["snippet"];
	        this.matches = source["matches"];
	        this.filePath = source["filePath"];
	        this.webUrl = source["webUrl"];
	    }
	}

}

