import * as vscode from "vscode";
import * as https from "https";
import * as http from "http";

function baseUrl(): string {
    return (vscode.workspace.getConfiguration("lmstudio").get<string>("baseUrl")
        ?? "http://192.168.1.153:1234/v1").replace(/\/$/, "");
}

// Minimal HTTP helper using Node built-ins — no external dependencies.
function jsonRequest(method: string, url: string, body?: object): Promise<unknown> {
    return new Promise((resolve, reject) => {
        const parsed = new URL(url);
        const lib = parsed.protocol === "https:" ? https : http;
        const payload = body ? Buffer.from(JSON.stringify(body)) : undefined;
        const req = lib.request(
            {
                hostname: parsed.hostname,
                port: parsed.port,
                path: parsed.pathname + parsed.search,
                method,
                headers: {
                    "Content-Type": "application/json",
                    ...(payload ? { "Content-Length": String(payload.byteLength) } : {}),
                },
            },
            (res) => {
                const chunks: Buffer[] = [];
                res.on("data", (c: Buffer) => chunks.push(c));
                res.on("end", () => {
                    try { resolve(JSON.parse(Buffer.concat(chunks).toString("utf8"))); }
                    catch (e) { reject(e); }
                });
            }
        );
        req.on("error", reject);
        if (payload) { req.write(payload); }
        req.end();
    });
}

interface LMStudioModel { id: string; }
interface ModelsResponse { data: LMStudioModel[]; }
interface ChatChoice {
    message: { content: string | null; reasoning_content?: string | null };
    finish_reason: string;
    delta?: { content?: string | null };
}
interface ChatResponse { choices: ChatChoice[]; model: string; usage?: object; }

async function fetchModels(): Promise<LMStudioModel[]> {
    const resp = await jsonRequest("GET", `${baseUrl()}/models`) as ModelsResponse;
    return (resp.data ?? []).filter(m => !m.id.includes("embed"));
}

function extractContent(choice: ChatChoice): string {
    return (choice.message?.content ?? "").trim()
        || (choice.message?.reasoning_content ?? "").trim();
}

async function chatCompletion(
    modelId: string,
    messages: readonly vscode.LanguageModelChatRequestMessage[],
    token: vscode.CancellationToken
): Promise<string> {
    if (token.isCancellationRequested) { throw new vscode.CancellationError(); }

    const apiMessages = messages.map(m => ({
        role: m.role === vscode.LanguageModelChatMessageRole.User ? "user"
            : m.role === vscode.LanguageModelChatMessageRole.Assistant ? "assistant"
            : "system",
        content: m.content
            .filter((p): p is vscode.LanguageModelTextPart => p instanceof vscode.LanguageModelTextPart)
            .map(p => p.value)
            .join(""),
    }));

    const resp = await jsonRequest("POST", `${baseUrl()}/chat/completions`, {
        model: modelId, messages: apiMessages, stream: false,
    }) as ChatResponse;

    const choice = resp.choices?.[0];
    if (!choice) { throw new Error("LM Studio returned no choices."); }
    return extractContent(choice);
}

class LMStudioProvider implements vscode.LanguageModelChatProvider {
    private _models: vscode.LanguageModelChatInformation[] = [];
    readonly onDidChangeLanguageModelChatInformation?: vscode.Event<void>;

    setModels(raw: LMStudioModel[]): void {
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

    provideLanguageModelChatInformation(
        _options: vscode.PrepareLanguageModelChatModelOptions,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.LanguageModelChatInformation[]> {
        return this._models;
    }

    async provideLanguageModelChatResponse(
        model: vscode.LanguageModelChatInformation,
        messages: readonly vscode.LanguageModelChatRequestMessage[],
        _options: object,
        progress: vscode.Progress<vscode.LanguageModelResponsePart>,
        token: vscode.CancellationToken
    ): Promise<void> {
        const text = await chatCompletion(model.id, messages, token);
        progress.report(new vscode.LanguageModelTextPart(text));
    }

    provideTokenCount(
        _model: vscode.LanguageModelChatInformation,
        text: string | vscode.LanguageModelChatRequestMessage,
        _token: vscode.CancellationToken
    ): Thenable<number> {
        // Rough heuristic: 4 chars ≈ 1 token
        const str = typeof text === "string" ? text
            : (text.content as vscode.LanguageModelTextPart[])
                .filter(p => p instanceof vscode.LanguageModelTextPart)
                .map(p => p.value).join("");
        return Promise.resolve(Math.ceil(str.length / 4));
    }
}

export async function activate(context: vscode.ExtensionContext): Promise<void> {
    let rawModels: LMStudioModel[];
    try {
        rawModels = await fetchModels();
    } catch (err) {
        vscode.window.showWarningMessage(
            `LM Studio: cannot reach ${baseUrl()} — models not registered. (${err})`
        );
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
    vscode.window.showInformationMessage(
        `LM Studio: registered ${rawModels.length} model(s) — ${names}`
    );
}

export function deactivate(): void { /* no-op */ }
