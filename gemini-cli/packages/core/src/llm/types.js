/**
 * Internal LLM type definitions replacing @google/genai usage.
 * Only includes shapes used by CodinGLM.
 */
export var FinishReason;
(function (FinishReason) {
    FinishReason["STOP"] = "STOP";
    FinishReason["MAX_TOKENS"] = "MAX_TOKENS";
    FinishReason["SAFETY"] = "SAFETY";
    FinishReason["FINISH_REASON_UNSPECIFIED"] = "FINISH_REASON_UNSPECIFIED";
})(FinishReason || (FinishReason = {}));
export class GenerateContentResponse {
    responseId;
    modelVersion;
    candidates = [];
    usageMetadata;
}
//# sourceMappingURL=types.js.map