import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";
import "./database-status.css";
import "./temporal.css";
import "./events.css";
import "./login.css";

const root = document.getElementById("root");
if (!root) throw new Error("WildTrack could not find its root element.");
createRoot(root).render(<StrictMode><App /></StrictMode>);
