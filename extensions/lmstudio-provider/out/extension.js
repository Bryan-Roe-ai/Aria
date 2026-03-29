"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const https = __importStar(require("https"));
const http = __importStar(require("http"));
function baseUrl() {
    return (vscode.workspace.getConfiguration("lmstudio").get("baseUrl")
        ?? "http://192.168.1.153:1234/v1").replace(/\/$/, "");
}
// Minimal HTTP helper using Node built-ins — no external dependencies.
function jsonRequest(method, url, body) {
    return new Promise((resolve, reject) => {
        const parsed = new URL(url);
        const lib = parsed.protocol === "https:" ? https : http;
        const payload = body ? Buffer.from(JSON.stringify(body)) : undefined;
        const req = lib.request({
            hostname: parsed.hostname,
            port: parsed.port,
            path: parsed.pathname + parsed.search,
            method,
            headers: {
                "Content-Type": "application/json",
                ...(payload ? { "Content-Length": String(payload.byteLength) } : {}),
            },
        }, (res) => {
            const chunks = [];
            res.on("data", (c) => chunks.push(c));
            res.on("end", () => {
                try {
                    resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")));
                }
                catch (e) {
                    reject(e);
                }
            });
        });
        req.on("error", reject);
        if (payload) {
            req.write(payload);
        }
        req.end();
    });
}
async function fetchModels() {
    const resp = await jsonRequest("GET", `${baseUrl()}/models`);
    return (resp.data ?? []).filter(m => !m.id.includes("embed"));
}
function extractContent(choice) {
    return (choice.message?.content ?? "").trim()
        || (choice.message?.reasoning_content ?? "").trim();
}
async function chatCompletion(modelId, messages, token) {
    if (token.isCancellationRequested) {
        throw new vscode.CancellationError();
    }
    const apiMessages = messages.map(m => ({
        role: m.role === vscode.LanguageModelChatMessageRole.User ? "user"
            : m.role === vscode.LanguageModelChatMessageRole.Assistant ? "assistant"
                : "system",
        content: m.content
            .filter((p) => p instanceof vscode.LanguageModelTextPart)
            .map(p => p.value)
            .join(""),
    }));
    const resp = await jsonRequest("POST", `${baseUrl()}/chat/completions`, {
        model: modelId, messages: apiMessages, stream: false,
    });
    const choice = resp.choices?.[0];
    if (!choice) {
        throw new Error("LM Studio returned no choices.");
    }
    return extractContent(choice);
}
class LMStudioProvider {
    constructor() {
        this._models = [];
    }
    setModels(raw) {
        this._models = raw.map(m => ({
            id: m.id,
            name: `LMStudio: ${m.id.split("/").pop() ?? m.id}`,
            family: m.id,
            version: "1.0",
            maxInputTokens: 8192,
            maxOutputTokens: 4096,
            capabilities: { toolCalling: false },
        }));
    }
    provideLanguageModelChatInformation(_options, _token) {
        return this._models;
    }
    async provideLanguageModelChatResponse(model, messages, _options, progress, token) {
        const text = await chatCompletion(model.id, messages, token);
        progress.report(new vscode.LanguageModelTextPart(text));
    }
    provideTokenCount(_model, text, _token) {
        // Rough heuristic: 4 chars ≈ 1 token
        const str = typeof text === "string" ? text
            : text.content
                .filter(p => p instanceof vscode.LanguageModelTextPart)
                .map(p => p.value).join("");
        return Promise.resolve(Math.ceil(str.length / 4));
    }
}
async function activate(context) {
    let rawModels;
    try {
        rawModels = await fetchModels();
    }
    catch (err) {
        vscode.window.showWarningMessage(`LM Studio: cannot reach ${baseUrl()} — models not registered. (${err})`);
        return;
    }
    if (rawModels.length === 0) {
        vscode.window.showWarningMessage("LM Studio: no chat models found.");
        return;
    }
    const provider = new LMStudioProvider();
    provider.setModels(rawModels);
    const disposable = vscode.lm.registerLanguageModelChatProvider("lmstudio", provider);
    context.subscriptions.push(disposable);
    const names = rawModels.map(m => m.id.split("/").pop()).join(", ");
    vscode.window.showInformationMessage(`LM Studio: registered ${rawModels.length} model(s) — ${names}`);
}
function deactivate() { }
