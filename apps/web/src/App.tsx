import { useEffect, useMemo, useState } from "react";

type Option = { id: string; label: string };
type StepState = {
  section_id: string;
  step_id: string;
  kind: "narration" | "modal" | "choice" | "dyn_choice" | string;
  text?: string | null;
  prompt?: string | null;
  options?: Option[];
  can_continue?: boolean;
  needs_input?: boolean;
};

const API_BASE =
  import.meta.env.VITE_BACKEND_URL?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

// pick a user id: ?uid=... (URL), else localStorage, else default
function useUserId(): string {
  const fromQuery = new URLSearchParams(window.location.search).get("uid");
  const stored = localStorage.getItem("aethel_uid");
  const uid = fromQuery || stored || "651758569380904961";
  useEffect(() => localStorage.setItem("aethel_uid", uid), [uid]);
  return uid;
}

async function postJson(path: string, body?: any) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  if (!res.ok) {
    // try to parse JSON error, else throw text
    try {
      const j = JSON.parse(text);
      throw new Error(j?.detail ? JSON.stringify(j.detail) : text);
    } catch {
      throw new Error(text || `HTTP ${res.status}`);
    }
  }
  try {
    return JSON.parse(text);
  } catch {
    // if server ever returned HTML or plain text by mistake
    throw new Error(`Invalid JSON from API: ${text.slice(0, 120)}…`);
  }
}

export default function App() {
  // Ensure white background so a CSS glitch never looks “black screen”
  useEffect(() => {
    document.body.style.background = "#fff";
    document.body.style.color = "#111";
    document.body.style.fontFamily =
      'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial';
  }, []);

  const uid = useUserId();
  const [step, setStep] = useState<StepState | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalValue, setModalValue] = useState("");

  // load/refresh current step
  const loadStart = async () => {
    setPending(true);
    setError(null);
    try {
      const s = await postJson(`/session/start?user_id=${encodeURIComponent(uid)}`);
      setStep(s);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setPending(false);
    }
  };

  useEffect(() => {
    loadStart();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid, API_BASE]);

  const onContinue = async () => {
    if (!step) return;
    setPending(true);
    setError(null);
    try {
      const s = await postJson(`/story/continue?user_id=${encodeURIComponent(uid)}`);
      setStep(s);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setPending(false);
    }
  };

  const onSubmitModal = async () => {
    if (!step) return;
    setPending(true);
    setError(null);
    try {
      const s = await postJson(`/story/submit`, { user_id: uid, value: modalValue });
      setStep(s);
      setModalValue("");
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setPending(false);
    }
  };

  const onChoose = async (option_id: string) => {
    if (!step) return;
    setPending(true);
    setError(null);
    try {
      const s = await postJson(`/story/choose`, { user_id: uid, option_id });
      setStep(s);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setPending(false);
    }
  };

  const options = useMemo(() => step?.options ?? [], [step]);

  return (
    <div style={{ maxWidth: 680, margin: "40px auto", padding: 16 }}>
      <h1 style={{ margin: "0 0 8px" }}>Aethelgard (dev)</h1>
      <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 16 }}>
        API: <code>{API_BASE}</code> &nbsp;|&nbsp; UID: <code>{uid}</code>{" "}
        <button
          style={{ marginLeft: 8 }}
          onClick={() => {
            localStorage.removeItem("aethel_uid");
            location.href = location.pathname; // reload without ?uid
          }}
        >
          reset uid
        </button>
      </div>

      {error && (
        <div style={{ background: "#fee", border: "1px solid #f99", padding: 12, marginBottom: 16, whiteSpace: "pre-wrap" }}>
          <b>API error:</b> {error}
        </div>
      )}

      {!step && !error && <div>Loading…</div>}

      {step && (
        <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16 }}>
          <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>
            step: <code>{step.step_id}</code> &middot; kind: <code>{step.kind}</code>
          </div>

          {/* NARRATION */}
          {step.kind === "narration" && (
            <>
              <p style={{ lineHeight: 1.5, whiteSpace: "pre-wrap" }}>{step.text || ""}</p>
              {step.can_continue && (
                <button onClick={onContinue} disabled={pending}>
                  {pending ? "…" : "Continue"}
                </button>
              )}
            </>
          )}

          {/* MODAL */}
          {step.kind === "modal" && (
            <>
              <div style={{ marginBottom: 8 }}>{step.prompt || "Enter value"}</div>
              <input
                value={modalValue}
                onChange={(e) => setModalValue(e.target.value)}
                placeholder="Type here"
                style={{ width: "100%", padding: 8, marginBottom: 8 }}
              />
              <button onClick={onSubmitModal} disabled={pending || !modalValue.trim()}>
                {pending ? "…" : "Submit"}
              </button>
            </>
          )}

          {/* CHOICE / DYN_CHOICE */}
          {(step.kind === "choice" || step.kind === "dyn_choice") && (
            <>
              <div style={{ marginBottom: 12 }}>{step.prompt || "Choose:"}</div>
              <div style={{ display: "grid", gap: 8 }}>
                {options.map((o) => (
                  <button key={o.id} onClick={() => onChoose(o.id)} disabled={pending} style={{ textAlign: "left", padding: "10px 12px" }}>
                    <div style={{ fontWeight: 600 }}>{o.label}</div>
                    <div style={{ fontSize: 12, opacity: 0.6 }}>{o.id}</div>
                  </button>
                ))}
              </div>
            </>
          )}

          {/* FALLBACK */}
          {!(["narration", "modal", "choice", "dyn_choice"] as string[]).includes(step.kind) && (
            <div>Under construction.</div>
          )}
        </div>
      )}

      {/* debug payload */}
      {step && (
        <details style={{ marginTop: 16 }}>
          <summary>Debug: raw step</summary>
          <pre style={{ background: "#f7f7f7", padding: 12, overflowX: "auto" }}>
            {JSON.stringify(step, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}