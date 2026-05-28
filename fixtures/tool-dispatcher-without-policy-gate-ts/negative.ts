export const t = {
  execute: async (args: any) => {
    const decision = await gov.decide({ resource: "x", args });
    if (decision.effect !== "permit") return "blocked";
    return doThing(args);
  },
};
declare const gov: { decide: (c: any) => Promise<{ effect: string }> };
function doThing(_a: any) { return "ok"; }
