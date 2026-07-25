// Precision fixtures for the Vercel AI SDK bounded-loop detector.
//   scope.agent-without-bounded-loop-ts  (detector, warning — existing rule)
import { generateText, streamText, stepCountIs } from "ai";

declare const model: any;
declare const tools: any;

// Bounded with maxSteps / stopWhen -> detector must NOT fire.
const bounded = await generateText({ model, tools, maxSteps: 5 }); // EXPECT_NONE:scope.agent-without-bounded-loop-ts
const boundedStream = await streamText({ model, tools, stopWhen: stepCountIs(5) }); // EXPECT_NONE:scope.agent-without-bounded-loop-ts

// Unbounded (tools present, no step cap) -> detector fires.
const unbounded = await generateText({ model, tools }); // EXPECT_MATCH:scope.agent-without-bounded-loop-ts
