// ProductDocumentation process entry point.
// Uses LM Studio (or any OpenAI-compatible endpoint) as the AI backend via Semantic Kernel.
// Provider priority: LMSTUDIO_BASE_URL env var → local fallback at http://host.docker.internal:1234/v1

using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel;
using Steps;

string lmStudioBaseUrl = Environment.GetEnvironmentVariable("LMSTUDIO_BASE_URL")
    ?? "http://host.docker.internal:1234/v1";
string modelId = Environment.GetEnvironmentVariable("LMSTUDIO_MODEL") ?? "local-model";

Console.WriteLine($"[ProductDocumentation] Using LM Studio at {lmStudioBaseUrl} (model: {modelId})");

// Build the Semantic Kernel with an OpenAI-compatible chat backend pointed at LM Studio.
IKernelBuilder kernelBuilder = Kernel.CreateBuilder();

kernelBuilder.Services.AddLogging(logging =>
    logging.AddConsole().SetMinimumLevel(LogLevel.Warning));

kernelBuilder.AddOpenAIChatCompletion(
    modelId: modelId,
    apiKey: "lm-studio",                 // LM Studio ignores the API key value
    endpoint: new Uri(lmStudioBaseUrl));

Kernel kernel = kernelBuilder.Build();

// Build the process from its step types.
ProcessBuilder processBuilder = new("ProductDocumentation");

ProcessStepBuilder getProductInfoStep = processBuilder.AddStepFromType<GetProductInfoStep>();
ProcessStepBuilder generateDocStep    = processBuilder.AddStepFromType<GenerateDocumentationStep>();
ProcessStepBuilder reviewDocStep      = processBuilder.AddStepFromType<ReviewDocumentationStep>();
ProcessStepBuilder publishDocStep     = processBuilder.AddStepFromType<PublishDocumentationStep>();

// --- Event graph ---
// 1. Process start → get product info
processBuilder
    .OnInputEvent("start")
    .SendEventTo(new ProcessFunctionTargetBuilder(getProductInfoStep));

// 2. Product info ready → generate first draft
getProductInfoStep
    .OnFunctionResult()
    .SendEventTo(new ProcessFunctionTargetBuilder(generateDocStep));

// 3. Draft ready → review
generateDocStep
    .OnFunctionResult()
    .SendEventTo(new ProcessFunctionTargetBuilder(reviewDocStep,
        parameterName: "documentation"));

// 4a. Review approved → publish
reviewDocStep
    .OnEvent(ReviewDocumentationStep.Events.Approved)
    .SendEventTo(new ProcessFunctionTargetBuilder(publishDocStep,
        parameterName: "reviewResult"));

// 4b. Review needs revision → regenerate with feedback (loop)
reviewDocStep
    .OnEvent(ReviewDocumentationStep.Events.NeedsRevision)
    .SendEventTo(new ProcessFunctionTargetBuilder(generateDocStep,
        functionName: nameof(GenerateDocumentationStep.RegenerateWithFeedbackAsync),
        parameterName: "reviewResult"));

// Run the process.
KernelProcess process = processBuilder.Build();
Console.WriteLine("[ProductDocumentation] Starting process...");

await using KernelProcessContext context = await process.StartAsync(
    kernel,
    new KernelProcessEvent { Id = "start", Data = "GlowBrew AI Coffee Machine" });

Console.WriteLine("[ProductDocumentation] Process completed. See published/ folder for output.");
