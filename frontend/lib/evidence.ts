const STOP = new Set(["است", "هست", "بود", "این", "آن", "که", "را", "از", "در", "به", "با", "برای", "های", "هر", "یا", "تا", "می", "شود", "شده", "باید", "کند"]);

const stems = (text: string) => {
  const out = new Set<string>();
  for (const w of text.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? []) {
    if (w.length < 3 || STOP.has(w)) continue;
    out.add(w.length >= 5 ? w.slice(0, 4) : w);
  }
  return out;
};

export type Piece = { text: string; evidence: boolean };

/**
 * Split a retrieved passage into sentences and flag the ones the answer actually used.
 * Works for verbatim (extractive) and paraphrased answers: a sentence counts as evidence
 * when most of its content words show up in the answer.
 */
export function markEvidence(passage: string, answer: string): Piece[] {
  const answerStems = stems(answer);
  const sentences = passage.split(/(?<=[.!؟?۔])\s+|\n+/).map((s) => s.trim()).filter(Boolean);

  const scored = sentences.map((text) => {
    const own = stems(text);
    let hit = 0;
    own.forEach((s) => answerStems.has(s) && hit++);
    return { text, own: own.size, ratio: own.size ? hit / own.size : 0 };
  });

  const strong = scored.map((s) => s.own >= 3 && s.ratio >= 0.6);
  if (!strong.some(Boolean)) {
    // paraphrased answer: fall back to the single best-matching sentence
    let best = -1;
    scored.forEach((s, i) => s.own >= 3 && s.ratio >= 0.3 && (best < 0 || s.ratio > scored[best].ratio) && (best = i));
    if (best >= 0) strong[best] = true;
  }
  return scored.map((s, i) => ({ text: s.text, evidence: strong[i] }));
}
