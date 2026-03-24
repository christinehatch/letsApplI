import React from "react";
import { useAuth0 } from "@auth0/auth0-react";

export function Auth0Controls() {
  const {
    isLoading,
    isAuthenticated,
    error,
    loginWithRedirect,
    logout,
    user,
  } = useAuth0();

  if (isLoading) {
    return (
      <div style={{ fontSize: "12px", color: "#666" }}>
        Auth loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        {error && (
          <span style={{ color: "#b91c1c", fontSize: "12px" }}>
            {error.message}
          </span>
        )}
        <button
          type="button"
          onClick={() =>
            loginWithRedirect({
              authorizationParams: { screen_hint: "signup" },
            })
          }
          style={buttonStyle}
        >
          Signup
        </button>
        <button
          type="button"
          onClick={() => loginWithRedirect()}
          style={buttonStyle}
        >
          Login
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      <span style={{ fontSize: "12px", color: "#334155" }}>
        {user?.email ?? "Authenticated user"}
      </span>
      <button
        type="button"
        onClick={() =>
          logout({ logoutParams: { returnTo: window.location.origin } })
        }
        style={buttonStyle}
      >
        Logout
      </button>
    </div>
  );
}

const buttonStyle: React.CSSProperties = {
  border: "1px solid #d1d5db",
  background: "#fff",
  borderRadius: "8px",
  padding: "6px 10px",
  cursor: "pointer",
  fontSize: "12px",
  fontWeight: 600,
  color: "#111827",
};
