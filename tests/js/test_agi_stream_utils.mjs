import assert from "node:assert/strict"
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import vm from "node:vm"
import { describe, it } from "node:test"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const UTILS_PATH = path.resolve(
    __dirname,
    "../../apps/chat/static/agi_stream_utils.js",
)

function loadAgiStreamUtils() {
    const source = fs.readFileSync(UTILS_PATH, "utf8")
    const context = { global: {} }
    vm.runInContext(source, vm.createContext(context))
    assert.ok(
        context.global.AGIStreamUtils,
        "AGIStreamUtils should attach to global",
    )
    return context.global.AGIStreamUtils
}

describe("AGIStreamUtils", () => {
    const { parseSSEText, prettyPrintDelta } = loadAgiStreamUtils()

    it("parseSSEText extracts delta payloads from SSE blocks", () => {
        const sse = [
            "event: meta",
            'data: {"provider":"agi"}',
            "",
            'data: {"delta":{"type":"analysis","data":"intent=coding"}}',
            "",
            'data: {"delta":{"type":"output","data":"Hello"}}',
            "",
            "data: [DONE]",
            "",
        ].join("\n")

        const deltas = parseSSEText(sse)
        assert.equal(deltas.length, 2)
        assert.equal(deltas[0].type, "analysis")
        assert.equal(deltas[1].type, "output")
        assert.equal(deltas[1].data, "Hello")
    })

    it("parseSSEText ignores malformed JSON lines", () => {
        const deltas = parseSSEText("data: not-json\n\n")
        assert.equal(deltas.length, 0)
    })

    it("prettyPrintDelta renders known delta types safely", () => {
        const html = prettyPrintDelta({
            type: "output",
            data: "<script>alert(1)</script>",
        })
        assert.match(html, /agi-output/)
        assert.doesNotMatch(html, /<script\b/i)
        assert.match(html, /&lt;script&gt;/)
    })

    it("prettyPrintDelta falls back for unknown delta types", () => {
        const html = prettyPrintDelta({ type: "unknown", data: { foo: "bar" } })
        assert.match(html, /agi-unknown/)
        assert.match(html, /foo/)
    })

    it("parseSSEText handles normalized string output deltas", () => {
        const sse = 'data: {"delta":{"type":"output","data":"Hi"}}\n\n'
        const deltas = parseSSEText(sse)
        assert.equal(deltas.length, 1)
        assert.equal(deltas[0].type, "output")
        assert.equal(deltas[0].data, "Hi")
    })
})
