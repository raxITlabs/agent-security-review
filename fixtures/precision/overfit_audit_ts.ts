// Regression fixture: rule-of-two-violation-ts was hardcoded to
// governed("stripe.payouts")-style literals; now keys on the generic trifecta
// (untrusted fetch + sensitive read + state-change/external send).
async function handler(userUrl: string) {
  const data = await fetch(userUrl);                 // [A] untrusted input  // EXPECT_MATCH:scope.rule-of-two-violation-ts
  const rows = await db.query("SELECT * FROM accounts");  // [B] sensitive read
  await mailer.sendMail({ to: "x", body: rows });    // [C] external send
}
