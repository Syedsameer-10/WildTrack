import { useState, type FormEvent } from "react";

export function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("Authentication connection is ready for the next step.");
  }

  return <section className="login-page" aria-labelledby="login-title">
    <div className="login-visual" aria-hidden="true">
      <div className="login-orbit orbit-a" /><div className="login-orbit orbit-b" />
      <span className="login-node node-a" /><span className="login-node node-b" /><span className="login-node node-c" />
      <div className="login-visual-copy"><p>SECURE FIELD ACCESS</p><strong>Every signal.<br />One protected view.</strong><span>Spatial zones · Temporal history · Active alerts</span></div>
    </div>
    <div className="login-card">
      <div className="login-card-heading"><span className="login-lock">W</span><p className="eyebrow">WILDTRACK OPERATIONS</p><h1 id="login-title">Welcome back.</h1><p>Sign in to access wildlife monitoring and response tools.</p></div>
      <form onSubmit={submit}>
        <label htmlFor="email">Email address</label>
        <input id="email" name="email" type="email" autoComplete="email" placeholder="ranger@wildtrack.org" required />
        <label htmlFor="password">Password</label>
        <div className="password-field"><input id="password" name="password" type={showPassword ? "text" : "password"} autoComplete="current-password" placeholder="Enter your password" minLength={8} required /><button type="button" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? "Hide" : "Show"}</button></div>
        <div className="login-options"><label><input type="checkbox" name="remember" /> Keep me signed in</label><a href="#/login">Forgot password?</a></div>
        <button className="login-submit" type="submit">Enter command center <span>→</span></button>
        {message && <p className="login-message" role="status">{message}</p>}
      </form>
      <p className="login-footnote"><span /> Protected access · Supabase Auth</p>
    </div>
  </section>;
}
