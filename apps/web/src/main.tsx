import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { error: any }> {
  constructor(props:any){ super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error:any){ return { error }; }
  componentDidCatch(error:any, info:any){ console.error("Render error:", error, info); }
  render(){
    if (this.state.error) {
      return (
        <pre style={{whiteSpace:"pre-wrap", background:"#fee", border:"1px solid #f99", padding:12}}>
{String(this.state.error?.message || this.state.error)}
        </pre>
      );
    }
    return this.props.children as any;
  }
}

const root = document.getElementById("root");
if (!root) {
  const d = document.createElement("pre");
  d.textContent = 'Missing <div id="root"> in index.html';
  document.body.appendChild(d);
} else {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>
  );
}
